import json
import unittest

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase


class TestUserService(BaseTestCase):
    """Tests for the Users Services."""

    def test_users(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/users/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """Ensure a new user can be added to the datatabase."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'eder',
                    'email': 'eder@eder.org'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('eder@eder.org was added', data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """
         A payload is not sent
         Ensure error is thrown if the JSON object is empty.
        """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """
        The payload is invalid
        the JSON object is empty or it contains the wrong keys
        """
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({'email': 'eder@eder.org'}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        """
        The user already exists in the database
        Ensure error is thrown if the email already exists.
        """
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'eder',
                    'email': 'eder@eder.org'
                }),
                content_type='application/json',
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'eder',
                    'email': 'eder@eder.org'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('That email already exists', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        """Ensure get single user behaves correctly"""
        user = User(username='eder', email='eder@eder.org')
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('eder', data['data']['username'])
            self.assertIn('eder@eder.org', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        """
        An id is not provided
        Ensure error is thrown if and id is not provided
        """
        with self.client:
            response = self.client.get('/users/happy')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        """
        The id does not exist
        Ensure error is thrown if the id does not exist
        """
        with self.client:
            response = self.client.get('/users/888')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])


if __name__ == '__main__':
    unittest.main()
