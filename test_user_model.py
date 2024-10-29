"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

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

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.user1 = User(
        email="user1@test.com",
        username="user1",
        password="HASHED_PASSWORD"
        )
        self.user2 = User(
            email="user2@test.com",
            username="user2",
            password="HASHED_PASSWORD"
        )

        db.session.add_all([self.user1, self.user2])
        db.session.commit()

        self.client = app.test_client()


    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    

    def test_repr_method(self):
        """Does the repr method work as expected?"""

        self.assertEqual(repr(self.user1), f"<User #{self.user1.id}: user1, user1@test.com>")

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""

        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_not_following(self):
        """Does is_following successfully detect when user1 is not following user2?"""

        self.assertFalse(self.user1.is_following(self.user2))

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""

        self.user2.following.append(self.user1)
        db.session.commit()

        self.assertTrue(self.user1.is_followed_by(self.user2))
        self.assertFalse(self.user2.is_followed_by(self.user1))

    def test_is_not_followed_by(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""

        self.assertFalse(self.user1.is_followed_by(self.user2))    