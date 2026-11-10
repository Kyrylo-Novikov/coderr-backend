from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser


class AccountTests(APITestCase):

    def setUp(self):
        self.url = reverse('registration')
        self.data = {'username': 'exampleUsername',
                     'email': 'example@mail.de', 'password': 'examplePassword', 'repeated_password': 'examplePassword', 'type': 'customer'}

    def test_create_account(self):
        '''
        Test user creation returns HTTP 201.
        '''
        response = self.client.post(self.url, self.data)
        self.assertTrue(CustomUser.objects.filter(
            email=self.data['email']).exists())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_account_invalid_email(self):
        '''
        Returns HTTP 400 Bad Request if the email is invalid.
        '''
        payload = self.data.copy()
        payload['email'] = 'test'
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_create_account_password_mismatch(self):
        '''
        Returns HTTP 400 Bad Request if the password do not match.
        '''
        payload = self.data.copy()
        payload['repeated_password'] = 'test'
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_create_account_duplicate_username(self):
        '''
        Returns HTTP 400 Bad Request if the username already used.
        '''
        response = self.client.post(self.url, self.data)
        payload = self.data.copy()
        payload['email'] = 'TestEmail@gmail.de'
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_create_account_duplicate_email(self):
        '''
        Returns HTTP 400 Bad Request if the email already used.
        '''
        response = self.client.post(self.url, self.data)
        payload = self.data.copy()
        payload['username'] = 'TestUser'
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
