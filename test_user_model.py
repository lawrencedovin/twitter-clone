"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

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

        user1 = User.signup("user1", "user1@gmail.com", "HASHED_PASSWORD", None)
        user2 = User.signup("user2", "user2@gmail.com", "123", None)

        db.session.commit()

        user1 = User.query.get(1)
        user2 = User.query.get(2)

        self.user1 = user1
        self.user2 = user2 

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

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
        # Tests if repr method for user is correct
        self.assertEqual(repr(test_user), '<User #3: test, test@gmail.com>')
        self.assertEqual(repr(self.user1), '<User #1: user1, user1@gmail.com>')
    
    ####
    #
    # Following tests
    #
    ####
    def test_user_follow(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user1.followers), 0)

        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)

        self.assertEqual(self.user1.following[0].id, self.user2.id)
        self.assertEqual(self.user2.followers[0].id, self.user1.id)
    
    def test_valid_signup(self):
        valid_user = User.signup('valid_user', 'valid_user@gmail.com', 'ketchup', None)
        valid_user.id = 123
        db.session.commit()

        validated_user = User.query.get(123)

        self.assertEqual(validated_user.username, 'valid_user')
        self.assertEqual(validated_user.email, 'valid_user@gmail.com')
        self.assertEqual(validated_user.id, 123)
        # Bcrypt strings should start with $2b$
        self.assertTrue(validated_user.password.startswith('$2b$'))
    
    def test_invalid_username(self):
        with self.assertRaises(exc.IntegrityError) as context:
            User.signup(None, 'invalid_user@gmail.com', 'pokemon', None)
            db.session.commit()
    
    def test_invalid_email(self):
        with self.assertRaises(exc.IntegrityError) as context:
            User.signup('invalid_user', None, 'pokemon', None)
            db.session.commit()
    
    def test_invalid_password(self):
        with self.assertRaises(ValueError) as context:
            User.signup('invalid_user', 'invalid_user@gmail.com', '', None)
            db.session.commit()

        with self.assertRaises(ValueError) as context:
            User.signup('invalid_user', 'invalid_user@gmail.com', None, None)
            db.session.commit()

    ####
    #
    # Authentication Tests
    #
    ####
    def test_valid_authentication(self):
        user1 = User.authenticate(self.user1.username, "HASHED_PASSWORD")
        self.assertIsNotNone(user1)
        self.assertEqual(user1.id, self.user1.id)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("pokeflute", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.user1.username, "badpassword"))