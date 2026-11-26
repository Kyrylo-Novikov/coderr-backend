
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import CustomUser
from offers_app.models import Offer, OfferDetail


class BaseTestSetUp(APITestCase):
    """Base set up for user and offer, with create method"""

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
                    "title": f"{offer_type.title()} Design",
                    "revisions": 2,
                    "delivery_time_in_days": days,
                    "price": price,
                    "features": ["Logo Design", "Visitenkarte"],
                    "offer_type": offer_type,
                }
                for offer_type, price, days in [("basic", 100, 2), ("standard", 500, 5), ("premium", 900, 8)]
            ],
        }
        self.user = CustomUser.objects.create_user(**self.user_data)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key)

    def create_offer(self, user=None):
        """
        Creates an offer with its 3 details in the database and returns the offer and the last detail.
        """
        offer = Offer.objects.create(
            user=user or self.user, title=self.offer_data['title'], description=self.offer_data['description']
        )
        detail = None
        for detail_data in self.offer_data['details']:
            detail = OfferDetail.objects.create(offer=offer, **detail_data)

        return offer, detail
