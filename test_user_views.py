"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

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

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.test_user = User.signup("test_user", "test_user@gmail.com", "123", None)
        self.secret = User.signup("secret", "secret@gmail.com", "password", None)
        self.user1 = User.signup("user1", "user1@gmail.com", "password", None)
        self.user2 = User.signup("user2", "user2@gmail.com", "password", None)
        self.user3 = User.signup("user3", "user3@gmail.com", "password", None)
        self.user4 = User.signup("user4", "user4@gmail.com", "password", None)
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_index(self):
        with self.client as client:
            response = client.get("/users")

            self.assertIn("@test_user", str(response.data))
            self.assertIn("@secret", str(response.data))
            self.assertIn("@user1", str(response.data))
            self.assertIn("@user2", str(response.data))
            self.assertIn("@user3", str(response.data))
            self.assertIn("@user4", str(response.data))

    def test_users_search(self):
        with self.client as client:
            response = client.get("/users?q=user")

            self.assertIn("@test_user", str(response.data))
            self.assertIn("@user1", str(response.data))
            self.assertIn("@user2", str(response.data))
            self.assertIn("@user3", str(response.data))
            self.assertIn("@user4", str(response.data))       

            self.assertNotIn("@secret", str(response.data))

    def test_user_page(self):
        with self.client as client:
            response = client.get(f"/users/{self.test_user.id}")

            self.assertEqual(response.status_code, 200)

            self.assertIn("@test_user", str(response.data))

    def setup_likes(self):
        message1 = Message(text="Pizza is good", user_id=self.user1.id)
        message2 = Message(text="Eating some lunch", user_id=self.user1.id)
        message3 = Message(id=123, text="Tweet tweet", user_id=self.user2.id)
        db.session.add_all([message1, message2, message3])
        db.session.commit()

        like1 = Likes(user_id=self.user1.id, message_id=123)

        db.session.add(like1)
        db.session.commit()

    # def test_user_show_with_likes(self):
    #     self.setup_likes()

    #     with self.client as client:
    #         response = client.get(f"/users/{self.user1.id}")

    #         self.assertEqual(response.status_code, 200)

    #         self.assertIn("@test_user", str(response.data))
    #         soup = BeautifulSoup(str(response.data), 'html.parser')
    #         found = soup.find_all("li", {"class": "stat"})
    #         self.assertEqual(len(found), 4)

    #         # test for a count of 2 messages
    #         self.assertIn("2", found[0].text)

    #         # Test for a count of 0 followers
    #         self.assertIn("0", found[1].text)

    #         # Test for a count of 0 following
    #         self.assertIn("0", found[2].text)

    #         # Test for a count of 1 like
    #         self.assertIn("1", found[3].text)

    def test_add_like(self):

        # Only works if route is redirected to "/" and not same page using request.referrer
        message = Message(id=1984, text="The earth is round", user_id=self.user1.id)
        db.session.add(message)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test_user.id

            response = client.post("/users/add_like/1984", follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==1984).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.test_user.id)