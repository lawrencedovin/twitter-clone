"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

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

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User(
            email="user1@gmail.com",
            username="user1",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            email="user2@gmail.com",
            username="user2",
            password="123"
        )

        db.session.add_all([user1, user2])
        db.session.commit()

        user1 = User.query.get(1)
        user2 = User.query.get(2)

        self.user1 = user1
        self.user2 = user2 

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        test_user = User(
            email="test@gmail.com",
            username="test",
            password="HASHED_PASSWORD"
        )

        db.session.add(test_user)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(test_user.messages), 0)
        self.assertEqual(len(test_user.followers), 0)
        self.assertEqual(repr(self.user1), '<User #1: user1, user1@gmail.com>')
    
    # def test_user_repr(self):
    #     self.assertEqual(repr(self.user1), '<User #1: user1, user1@gmail.com>')