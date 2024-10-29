"""Message model tests."""

import os
from unittest import TestCase
from models import db, Message, User, Likes

# Set the test database environment variable
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

# Create all tables once for testing
db.create_all()

class MessageModelTestCase(TestCase):
    """Test models for messages."""

    def setUp(self):
        """Create test client and sample data."""
        
        # Clear any previous test data
        User.query.delete()
        Message.query.delete()
        Likes.query.delete()

        # Set up test client
        self.client = app.test_client()

        # Create a test user
        self.testuser = User.signup(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD",
            image_url=None
        )
        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()

    def test_message_model(self):
        """Does basic message creation work?"""

        # Create a new message for the test user
        msg = Message(
            text="Test message",
            user_id=self.testuser.id
        )

        db.session.add(msg)
        db.session.commit()

        # Test: Ensure the message is created
        self.assertEqual(len(self.testuser.messages), 1)
        self.assertEqual(self.testuser.messages[0].text, "Test message")

    def test_message_user_relationship(self):
        """Does the message-user relationship work?"""

        # Create another message for the test user
        msg = Message(
            text="Another test message",
            user_id=self.testuser.id
        )

        db.session.add(msg)
        db.session.commit()

        # Test: Check if the message belongs to the correct user
        self.assertEqual(msg.user.username, "testuser")

    def test_user_likes_message(self):
        """Can a user like a message?"""

        # Create a second user to like the message
        user2 = User.signup(
            username="otheruser",
            email="other@test.com",
            password="PASSWORD",
            image_url=None
        )
        db.session.commit()

        # Create a message
        msg = Message(
            text="Message to like",
            user_id=self.testuser.id
        )
        db.session.add(msg)
        db.session.commit()

        # User2 likes the message
        user2.likes.append(msg)
        db.session.commit()

        # Test: Check if the like was successfully added
        self.assertEqual(len(user2.likes), 1)
        self.assertEqual(user2.likes[0].id, msg.id)

    def test_user_unlikes_message(self):
        """Can a user unlike a message?"""

        # Create a second user to like/unlike the message
        user2 = User.signup(
            username="otheruser2",
            email="other2@test.com",
            password="PASSWORD",
            image_url=None
        )
        db.session.commit()

        # Create a message
        msg = Message(
            text="Message to unlike",
            user_id=self.testuser.id
        )
        db.session.add(msg)
        db.session.commit()

        # User2 likes the message
        user2.likes.append(msg)
        db.session.commit()

        # Now user2 unlikes the message
        user2.likes.remove(msg)
        db.session.commit()

        # Test: Check if the message was unliked
        self.assertEqual(len(user2.likes), 0)