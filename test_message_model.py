"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        test_user = User.signup("test_user", "test_user@gmail.com", "password", None)
        db.session.commit()

        self.test_user = User.query.get(test_user.id)

        self.client = app.test_client()

    def tearDown(self):
        response = super().tearDown()
        db.session.rollback()
        return response

    def test_message_model(self):
        """Does basic model work?"""
        
        message = Message(text="Warble warble", user_id=self.test_user.id)

        db.session.add(message)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(self.test_user.messages), 1)
        self.assertEqual(self.test_user.messages[0].text, "Warble warble")

    def test_message_likes(self):
        message1 = Message(
            text="Warble warble",
            user_id=self.test_user.id
        )

        message2 = Message(
            text="Insert warble here",
            user_id=self.test_user.id
        )

        ashe = User.signup("ashe_ketchup", "ashe_ketchup@pokemon.com", "password", None)
        db.session.add_all([message1, message2, ashe])
        db.session.commit()

        ashe.likes.append(message1)

        db.session.commit()

        likes = Likes.query.filter(Likes.user_id == ashe.id).all()
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].message_id, message1.id)