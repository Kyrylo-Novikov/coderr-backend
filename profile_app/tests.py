from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from profile_app.models import Profile


class ProfileTests(APITestCase):

    """
    Tests for retrieving and patching user profiles.
    """

    def setUp(self):
        """
        Creates a user  with a profile and a token, and authenticates the client.
        """
        self.data = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "type": "customer",
        }
        self.user = CustomUser.objects.create_user(**self.data)
        self.profile = Profile.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_profile(self):
        """
        Successfully retrieve data from the chosen profile
        """
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.profile.user.username, response.data["username"])
        self.assertEqual(self.profile.user.id, response.data["user"])
        self.assertEqual(self.profile.user.first_name,
                         response.data["first_name"])
        self.assertIn("profile_default.jpg", response.data["file"])
        self.assertEqual(self.profile.location, response.data["location"])
        self.assertEqual(self.profile.tel, response.data["tel"])
        self.assertEqual(self.profile.description,
                         response.data["description"])
        self.assertEqual(self.profile.working_hours,
                         response.data["working_hours"])
        self.assertEqual(self.profile.user.type, response.data["type"])
        self.assertEqual(self.profile.user.email, response.data["email"])
        self.assertIn("created_at", response.data)

    def test_get_profile_unauthenticated(self):
        """
        Rejects a GET without valid credentials.
        """
        self.client.credentials()
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('username', response.data)
        self.assertNotIn('email', response.data)

    def test_get_profile_not_found(self):
        """
        Rejects retrieving a profile thet does not exist.
        """
        url = reverse('profile-detail', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotIn('username', response.data)
        self.assertNotIn('email', response.data)

    def test_patch_profile(self):
        """
        Updates profile and user fields partially and returns the updated data.
        """
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        payload = {
            "first_name": "Max",
            "last_name": "Mustermann",
            "email": "max@mail.de",
            "location": "Berlin",
            "tel": "+491701234567",
            "description": "Fullstack developer",
            "working_hours": "9-17",
        }
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEqual(self.user, self.profile.user)
        self.assertEqual(self.profile.location, "Berlin")
        self.assertEqual(self.profile.tel, "+491701234567")
        self.assertEqual(self.profile.description, "Fullstack developer")
        self.assertEqual(self.profile.working_hours, "9-17")
        self.assertEqual(self.user.first_name, "Max")
        self.assertEqual(self.user.last_name, "Mustermann")
        self.assertEqual(self.user.email, "max@mail.de")

        self.assertEqual(response.data["first_name"], "Max")
        self.assertEqual(response.data["location"], "Berlin")
        self.assertEqual(response.data["email"], "max@mail.de")

    def test_patch_read_only_fields_unchanged(self):
        """
        Ignores read-only fields sent in the payload.
        """
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        created_at = self.client.get(url).data['created_at']
        payload = {
            "username": "hackedUsername",
            "type": "business",
            "user": 999,
            "created_at": "2020-01-01T00:00:00Z",
        }
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'exampleUsername')
        self.assertEqual(self.user.type, 'customer')
        self.assertEqual(self.profile.user_id, self.user.id)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['created_at'], created_at)

    def test_patch_profile_unauthenticated(self):
        """
        Reject a PATCH without valid credentials.
        """
        self.client.credentials()
        url = reverse('profile-detail', kwargs={'pk': self.user.id})
        payload = {
            "first_name": "Max",
            "location": "Berlin",
        }
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('username', response.data)
        self.assertNotIn('email', response.data)
        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.profile.location, '')
        self.assertEqual(self.user.first_name, '')

    def test_patch_other_profile_forbidden(self):
        """
        Rejects a PATCH on a profile that belongs to another user.
        """
        other_user = CustomUser.objects.create_user(
            username="otherUsername",
            email="other@mail.de",
            password="otherPassword",
            type="customer",
        )
        other_profile = Profile.objects.create(user=other_user)
        url = reverse('profile-detail', kwargs={'pk': other_user.id})
        payload = {
            "first_name": "Max",
            "location": "Berlin",
        }
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn('username', response.data)
        self.assertNotIn('email', response.data)
        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(other_profile.location, '')
        self.assertEqual(other_user.first_name, '')
        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.profile.location, '')
        self.assertEqual(self.user.first_name, '')

    def test_patch_profile_not_found(self):
        """
        Returns 404 when patching a profile that does not exist.
        """
        url = reverse('profile-detail', kwargs={'pk': 999})
        payload = {
            "first_name": "Max",
            "location": "Berlin",
        }
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotIn('username', response.data)
        self.assertNotIn('email', response.data)
        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.profile.location, '')
        self.assertEqual(self.user.first_name, '')
