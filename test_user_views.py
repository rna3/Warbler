"""View function tests for authentication and authorization."""

import os
from unittest import TestCase

from models import db, connect_db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class ViewFunctionTestCase(TestCase):
    """Test views for Warbler app."""

    def setUp(self):
        """Create test client, add sample data."""
        
        # Delete all data before starting the tests
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        # Create a test client
        self.client = app.test_client()

        # Create a test user
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        # Create a second user for testing follower/following features
        self.otheruser = User.signup(username="otheruser",
                                     email="other@test.com",
                                     password="otheruser",
                                     image_url=None)

        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()

    # 1. Test: When logged in, can you see the follower/following pages for any user?
    def test_follower_following_pages_logged_in(self):
        """Can a logged-in user view the follower/following pages for any user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Access the follower and following pages for the other user
            resp_follower = c.get(f"/users/{self.otheruser.id}/followers")
            resp_following = c.get(f"/users/{self.otheruser.id}/following")

            # Check if the responses are OK (200)
            self.assertEqual(resp_follower.status_code, 200)
            self.assertEqual(resp_following.status_code, 200)

            # Check for expected HTML content
            self.assertIn("Followers", str(resp_follower.data))
            self.assertIn("Following", str(resp_following.data))

    # 2. Test: When logged out, are you disallowed from visiting a user's follower/following pages?
    def test_follower_following_pages_logged_out(self):
        """Is a logged-out user disallowed from visiting follower/following pages?"""

        with self.client as c:
            resp_follower = c.get(f"/users/{self.otheruser.id}/followers", follow_redirects=True)
            resp_following = c.get(f"/users/{self.otheruser.id}/following", follow_redirects=True)

            # Check if the user is redirected to the login page
            self.assertEqual(resp_follower.status_code, 200)
            self.assertIn("Access unauthorized", str(resp_follower.data))

            self.assertEqual(resp_following.status_code, 200)
            self.assertIn("Access unauthorized", str(resp_following.data))

    # 3. Test: When logged in, can you add a message as yourself?
    def test_add_message_logged_in(self):
        """Can a logged-in user add a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Post a new message
            resp = c.post("/messages/new", data={"text": "Hello, world!"}, follow_redirects=True)

            # Ensure it redirects and the message was added
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Hello, world!", str(resp.data))

            # Ensure the message is stored in the database
            msg = Message.query.filter_by(text="Hello, world!").first()
            self.assertIsNotNone(msg)
            self.assertEqual(msg.user_id, self.testuser.id)

    # 4. Test: When logged in, can you delete a message as yourself?
    def test_delete_message_logged_in(self):
        """Can a logged-in user delete their own message?"""

        # Add a message to the database
        msg = Message(text="To be deleted", user_id=self.testuser.id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Send a post request to delete the message
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)

            # Ensure the message was deleted
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Message deleted", str(resp.data))

            # Ensure the message is no longer in the database
            deleted_msg = Message.query.get(msg.id)
            self.assertIsNone(deleted_msg)

    # 5. Test: When logged out, are you prohibited from adding messages?
    def test_add_message_logged_out(self):
        """Is a logged-out user prohibited from adding a message?"""

        with self.client as c:
            # Attempt to post a new message without being logged in
            resp = c.post("/messages/new", data={"text": "Not allowed"}, follow_redirects=True)

            # Ensure the user is redirected and an error message is shown
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            # Ensure the message is not stored in the database
            msg = Message.query.filter_by(text="Not allowed").first()
            self.assertIsNone(msg)