
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import CustomUser

from .base import BaseTestSetUp


class OffersDetailTests(BaseTestSetUp, APITestCase):
    """
    Test suite for retrieving , patching  and deleting a singel offer
    """

    def setUp(self):
        """
        Sets up a test offer and a corresponding detail endpoint
        """
        super().setUp()
        self.offer, self.detail = self.create_offer()
        self.url = reverse('offers-detail', kwargs={"id": self.offer.id})
        self.patch_data = {
            "title": "Updated Grafikdesign-Paket",
            "details": [
                {
                    "title": "Basic Design Updated",
                    "revisions": 3,
                    "delivery_time_in_days": 6,
                    "price": 120,
                    "features": [
                        "Logo Design",
                        "Flyer"
                    ],
                    "offer_type": "basic"
                }
            ]
        }

    def test_get_single_offer(self):
        """
        Successfully retrieves a single offer.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['min_price'], 100.00)
        self.assertEqual(response.data['min_delivery_time'], 2)
        self.assertEqual(response.data['title'], "Grafikdesign-Paket")
        self.assertEqual(len(response.data['details']), 3)
        self.assertNotIn('user_details', response.data)

    def test_get_single_offer_unauthenticated(self):
        """
        Reject retrieving from an unauthenticated user.
        """
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertNotIn('id', response.data)
        self.assertNotIn('title', response.data)
        self.assertNotIn('details', response.data)

    def test_get_single_offer_not_found(self):
        """
        Reject retrieving of an not exiting offer.
        """
        self.url = reverse('offers-detail', kwargs={"id": 999})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
        self.assertNotIn('id', response.data)
        self.assertNotIn('title', response.data)
        self.assertNotIn('details', response.data)

    def test_patch_single_offer(self):
        """
        Successfully patch a single offer.
        """
        response = self.client.patch(self.url, self.patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Updated Grafikdesign-Paket")
        self.assertEqual(response.data['details']
                         [0]['delivery_time_in_days'], 6)
        self.assertEqual(response.data['details']
                         [0]['offer_type'], self.patch_data['details']
                         [0]['offer_type'])
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, "Updated Grafikdesign-Paket")
        self.assertNotIn('user_details', response.data)

    def test_patch_single_offer_unauthenticated(self):
        """
        Reject patch request if the user is unauthenticated
        """
        self.client.credentials()
        response = self.client.patch(self.url, self.patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.offer.refresh_from_db()
        self.assertNotEqual(self.offer.title, "Updated Grafikdesign-Paket")
        self.assertNotIn('user_details', response.data)
        self.assertIn('detail', response.data)
        self.assertNotIn('id', response.data)
        self.assertNotIn('title', response.data)
        self.assertNotIn('details', response.data)

    def test_patch_single_offer_not_owner(self):
        """
        Rejects patch requests from users who do not own the offer.
        """
        other_user = CustomUser.objects.create_user({
            "username": "otherExampleUsername",
            "email": "otherExample@mail.de",
            "password": "otherExamplePassword",
            "type": "business",
        })
        other_offer, _ = self.create_offer(user=other_user)
        self.url = reverse('offers-detail', kwargs={"id": other_offer.id})
        response = self.client.patch(
            self.url, {"title": "Gehackter Titel"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        other_offer.refresh_from_db()
        self.assertNotEqual(other_offer.title, "Gehackter Titel")

    def test_patch_single_offer_invalid_data(self):
        """
        Reject PATCH requests with HTTP 400 Bad Request for invalid payloads.
        """
        invalide_cases = [
            ("missing_offer_type", {"details": [{"price": 150}]}),
            ("invalid_offer_type", {"details": [
                {"offer_type": "vip", "price": 150}]}),
            ("invalid_price_type", {"details": [
                {"offer_type": "basic", "price": "teuer"}]})
        ]

        for case_name, payload in invalide_cases:
            with self.subTest(case=case_name):
                response = self.client.patch(self.url, payload, format="json")
                self.assertEqual(response.status_code,
                                 status.HTTP_400_BAD_REQUEST)

    def test_patch_single_offer_not_found(self):
        """
        Reject patching of a not foundet offer
        """
        self.url = reverse('offers-detail', kwargs={"id": 999})
        response = self.client.patch(
            self.url, {"title": "Gehackter Titel"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_single_offer(self):
        """
        Tests deleting of an offer
        """
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_single_offer_not_owner(self):
        """
        Rejects deleting requests from user who do not owne the offer.
        """
        other_user = CustomUser.objects.create_user({
            "username": "otherExampleUsername",
            "email": "otherExample@mail.de",
            "password": "otherExamplePassword",
            "type": "business",
        })
        other_offer, _ = self.create_offer(user=other_user)
        self.url = reverse('offers-detail', kwargs={"id": other_offer.id})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_single_offer_unauthenticated(self):
        """
        Reject deleting request if the user is unauthenticated
        """
        self.client.credentials()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_single_offer_not_found(self):
        """
        Reject deleting of a not foundet offer
        """
        self.url = reverse('offers-detail', kwargs={"id": 999})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
