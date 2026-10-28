from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User


class AccountsAPITests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.refresh_url = reverse('token_refresh')
        self.valid_payload = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123'
        }

    def test_user_registration_success(self):
        response = self.client.post(self.register_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'testuser@example.com')
        self.assertNotIn('password', response.data)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_registration_missing_email(self):
        payload = {
            'username': 'noemailuser',
            'password': 'password123'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_duplicate_username(self):
        self.client.post(self.register_url, self.valid_payload)
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_registration_duplicate_email(self):
        self.client.post(self.register_url, self.valid_payload)
        response = self.client.post(self.register_url, {
            'username': 'differentuser',
            'email': 'testuser@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_short_password(self):
        payload = {
            'username': 'shortpassuser',
            'email': 'shortpass@example.com',
            'password': '123'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_jwt_login_success(self):
        User.objects.create_user(
            username='loginuser',
            email='loginuser@example.com',
            password='securepassword'
        )
        response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'securepassword'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_jwt_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_success(self):
        User.objects.create_user(
            username='refresher',
            email='refresher@example.com',
            password='securepassword'
        )
        login_res = self.client.post(self.login_url, {
            'username': 'refresher',
            'password': 'securepassword'
        })
        refresh_token = login_res.data['refresh']

        response = self.client.post(self.refresh_url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_invalid_token(self):
        response = self.client.post(self.refresh_url, {'refresh': 'invalid_token_string'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_missing_token(self):
        response = self.client.post(self.refresh_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_blank_username(self):
        response = self.client.post(self.register_url, {
            'username': '   ',
            'email': 'blanku@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_registration_invalid_email(self):
        response = self.client.post(self.register_url, {
            'username': 'invalidemailuser',
            'email': 'not-a-valid-email',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registration_whitespace_padded_duplicate_username(self):
        self.client.post(self.register_url, self.valid_payload)
        response = self.client.post(self.register_url, {
            'username': '  testuser  ',
            'email': 'other@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_registration_case_insensitive_duplicate_email(self):
        self.client.post(self.register_url, self.valid_payload)
        response = self.client.post(self.register_url, {
            'username': 'caseuser',
            'email': 'TESTUSER@EXAMPLE.COM',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registration_whitespace_password(self):
        response = self.client.post(self.register_url, {
            'username': 'spacesuser',
            'email': 'spaces@example.com',
            'password': '      '
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

