
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .base import BaseTestSetUp


class OfferDetailsTests(BaseTestSetUp, APITestCase):
    """
    Tests the retrieving of the offer details
    """

    def setUp(self):
        """
        Sets up a test offer with its details.
        """
        super().setUp()
        self.offer, self.detail = self.create_offer()

    def test_get_offerdetails(self):
        """
        Successfully retrieves a single offer detail.
        """
        url = reverse('offerdetails-detail',
                      kwargs={'id': self.detail.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.detail.pk)
        self.assertEqual(response.data['title'], self.detail.title)
        self.assertEqual(response.data['offer_type'], 'premium')
        self.assertEqual(response.data['price'], '900.00')

    def test_get_offerdetails_unauthenticated(self):
        """
        Reject detail retrivieng for unauthenticated user
        """
        self.client.credentials()
        url = reverse('offerdetails-detail',
                      kwargs={'id': self.detail.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('id', response.data)

    def test_get_offerdetails_not_found(self):
        """
        Returns 404 for an unknown offer detail id.
        """
        url = reverse('offerdetails-detail',
                      kwargs={'id': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotIn('id', response.data)
