
import copy

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail


class BaseTestSetUp(APITestCase):
    def setUp(self):
        self.user_data = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "type": "business",
        }
        self.offer_data = {
            "title": "Grafikdesign-Paket",
            "description": "Ein umfassendes Grafikdesign-Paket für Unternehmen.",
            "details": [
                {
                     "title": "Basic Design",
                     "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": [
                        "Logo Design",
                        "Visitenkarte"
                    ],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Design",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": [
                        "Logo Design",
                        "Visitenkarte",
                        "Briefpapier"
                    ],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium Design",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": [
                        "Logo Design",
                        "Visitenkarte",
                        "Briefpapier",
                        "Flyer"
                    ],
                    "offer_type": "premium"
                }
            ]
        }
        self.user = CustomUser.objects.create_user(**self.user_data)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key)


class OffersTests(BaseTestSetUp, APITestCase):
    """
    Tests for retrieving and creating offer
    """

    def setUp(self):
        """
        Set up data for the user with authtoken, password and type  and set uop data for the offer.
        """
        super().setUp()
        self.url = reverse('offers-list')

    def test_post_offer(self):
        """
        Successfully creates a offer with title, description, image, and 3 specific offer details.
        """
        response = self.client.post(self.url, self.offer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['details']), 3)
        self.assertEqual(response.data['title'], self.offer_data['title'])
        self.assertEqual(response.data['description'],
                         self.offer_data['description'])
        self.assertIn('image', response.data)
        self.assertIn('id', response.data)
        self.assertIsNone(response.data['image'])
        self.assertNotIn('user', response.data)
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 3)
        self.assertEqual(Offer.objects.get().user, self.user)

    def test_post_offer_unauthenticated(self):
        """
        Reject post requests from an unauthenticated user.
        """
        self.client.credentials()
        response = self.client.post(self.url, self.offer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertNotIn('id', response.data)
        self.assertNotIn('title', response.data)
        self.assertNotIn('details', response.data)

    def test_post_offer_customer_user(self):
        """
        Reject post requests from user with other types as business.
        """
        self.user.type = 'customer'
        self.user.save()
        response = self.client.post(self.url, self.offer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)
        self.assertNotIn('id', response.data)
        self.assertNotIn('title', response.data)
        self.assertNotIn('details', response.data)

    def test_post_offer_missing_title(self):
        """
        Reject post requests if title is missing
        """
        payloade = self.offer_data.copy()
        payloade.pop('title')
        response = self.client.post(self.url, payloade, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_offer_missing_description(self):
        """
        Reject post requests if description is missing
        """
        payloade = self.offer_data.copy()
        payloade.pop('description')
        response = self.client.post(self.url, payloade, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_offer_missing_details(self):
        """
        Reject post requests if details is missing
        """
        payloade = self.offer_data.copy()
        payloade.pop('details')
        response = self.client.post(self.url, payloade, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_offer_not_enough_details(self):
        """
        Reject post requests if details does not contain 3 items
        """
        payloade = self.offer_data.copy()
        payloade['details'] = self.offer_data['details'][:2]
        response = self.client.post(self.url, payloade, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('details', response.data)

    def test_post_offer_missing_detail_field(self):
        """
        Reject post requests if detail field is missing
        """
        payloade = copy.deepcopy(self.offer_data)
        payloade['details'][0].pop('price')
        response = self.client.post(self.url, payloade, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_offers(self):
        """
        Tests retrievieng the infomations of the offers
        """
        offer = Offer.objects.create(
            user=self.user,
            title="Grafikdesign-Paket",
            description="Beschreibung",
        )
        for offer_type in ("basic", "standard", "premium"):
            OfferDetail.objects.create(
                offer=offer, title=f"{offer_type.title()} Design", revisions=2,
                delivery_time_in_days=5, price=100,
                features=["Logo"], offer_type=offer_type,
            )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Grafikdesign-Paket")
        self.assertEqual(len(response.data[0]['details']), 3)

    def test_get_offers_customer(self):
        """
        Tests retrievieng offers as customer
        """
        self.user.type = 'customer'
        self.user.save()
        response = self.client.get(self.url)
        print(self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OfferDetailsTests(BaseTestSetUp, APITestCase):
    """
    Tests the retrieving of the offer details
    """

    def setUp(self):
        super().setUp()
        offer = Offer.objects.create(
            user=self.user,
            title="Grafikdesign-Paket",
            description="Beschreibung",
        )
        # for offer_type in ("basic", "standard", "premium"):
        self.detail = OfferDetail.objects.create(
            offer=offer, title=f"Basic Design", revisions=2,
            delivery_time_in_days=5, price=100,
            features=["Logo"], offer_type="basic",
        )

    def test_get_offerdetails(self):
        """
        Successfully retrieview a offer detail
        """
        url = reverse('offerdetails-detail',
                      kwargs={'id': self.detail.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.detail.pk)
        self.assertEqual(response.data['title'], self.detail.title)
        self.assertEqual(response.data['offer_type'], 'basic')
        self.assertEqual(response.data['price'], '100.00')

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
        Return 404 for an unknowen offer detail id
        """
        url = reverse('offerdetails-detail',
                      kwargs={'id': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotIn('id', response.data)
