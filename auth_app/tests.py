from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CustomUser


class RegistrationTests(APITestCase):
    """
    Tests the registration cases.
    """

    def setUp(self):
        self.url = reverse("registration")
        self.data = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer",
        }

    def test_create_account(self):
        """
        Test successful user creation,returns an auth token, the email, and user id.
        """
        response = self.client.post(self.url, self.data)
        self.assertTrue(CustomUser.objects.filter(
            email=self.data["email"]).exists())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.data['username'], response.data["username"])
        self.assertIn("token", response.data)
        self.assertIn("user_id", response.data)
        self.assertNotIn("repeated_password", response.data)
        self.assertNotIn("password", response.data)

    def test_create_account_invalid_email(self):
        """
        Rejects registration if the the email format is invalid.
        """
        payload = self.data.copy()
        payload["email"] = "test"
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_create_account_password_mismatch(self):
        """
        Rejects registration if the password do not match.
        """
        payload = self.data.copy()
        payload["repeated_password"] = "test"
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_create_account_duplicate_username(self):
        """
        Prevents the registration of duplicate usernames.
        """
        response = self.client.post(self.url, self.data)
        payload = self.data.copy()
        payload["email"] = "TestEmail@gmail.de"
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_create_account_duplicate_email(self):
        """
        Prevents the registration of duplicate email.
        """
        response = self.client.post(self.url, self.data)
        payload = self.data.copy()
        payload["username"] = "TestUser"
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
