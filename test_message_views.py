"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_no_session(self):
        with self.client as client:
            response = client.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Access unauthorized", str(response.data))

    def test_add_invalid_user(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 350 # user does not exist

            response = client.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Access unauthorized", str(response.data))

    def test_message_show(self):

        message = Message(
            id=1234,
            text="I want pizza",
            user_id=self.testuser.id
        )
        
        db.session.add(message)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            message = Message.query.get(1234)

            response = client.get(f'/messages/{message.id}')

            self.assertEqual(response.status_code, 200)
            self.assertIn(message.text, str(response.data))

    def test_invalid_message_show(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            response = client.get('/messages/99999999')

            self.assertEqual(response.status_code, 404)

    def test_message_delete(self):

        message = Message(
            id=1234,
            text="Reeses",
            user_id=self.testuser.id
        )
        db.session.add(message)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            response = client.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            message = Message.query.get(1234)
            self.assertIsNone(message)

    def test_unauthorized_message_delete(self):

        # A second user that will try to delete the message
        user = User.signup(username="haxorsz",
                        email="haxorsz@test.com",
                        password="password",
                        image_url=None)
        user.id = 76543

        #Message is owned by testuser
        message = Message(
            id=1234,
            text="Testing 123 testing mic check",
            user_id=self.testuser.id
        )

        db.session.add_all([user, message])
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 76543

            response = client.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Access unauthorized", str(response.data))

            message = Message.query.get(1234)
            self.assertIsNotNone(message)

    def test_message_delete_no_authentication(self):

        message = Message(
            id=1234,
            text="Ranch",
            user_id=self.testuser.id
        )

        db.session.add(message)
        db.session.commit()

        with self.client as client:
            response = client.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Access unauthorized", str(response.data))

            message = Message.query.get(1234)
            self.assertIsNotNone(message)
