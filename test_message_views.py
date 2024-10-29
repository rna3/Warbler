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
        
        self.otheruser = User.signup(username="otheruser",
                                     email="other@test.com",
                                     password="otheruser",
                                     image_url=None)

        db.session.commit()


    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()


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
            self.assertEqual(msg.user_id, self.testuser.id)

    def test_add_message_logged_out(self):
        """Is a logged-out user prohibited from adding a message?"""

        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)

            # Check that the user is redirected to the login page
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))


    def test_view_message(self):
        """Can anyone view a specific message?"""

        # Create a message as the test user
        msg = Message(text="Hello", user_id=self.testuser.id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            # Access the message page
            resp = c.get(f"/messages/{msg.id}")

            # Check if the message content is visible
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Hello", str(resp.data))


    def test_delete_message(self):
        """Can a logged-in user delete their own message?"""

        # Create a message as the test user
        msg = Message(text="Delete me", user_id=self.testuser.id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            # Log in as the test user
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Send a post request to delete the message
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)

            # Check if the message was deleted
            self.assertEqual(Message.query.get(msg.id), None)
            

    def test_unauthorized_message_delete(self):
        """Is a user prevented from deleting another user's message?"""

        # Create a message as the test user
        msg = Message(text="No deleting me", user_id=self.testuser.id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            # Log in as a different user
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.otheruser.id

            # Try to delete the message
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)

            # Ensure unauthorized access is forbidden
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            # Ensure the message is still in the database
            self.assertIsNotNone(Message.query.get(msg.id))