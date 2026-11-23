from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from offers_app.models import Offer, OfferDetail

from .permissions import IsBusinessUserOrReadOnly
from .serializers import OffersCreateSerializer, OffersGetSerializer, OfferDetailSerializer


class OffersView(generics.ListCreateAPIView):
    """
    API view for listing all offers and creating a new offer.
    """
    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated, IsBusinessUserOrReadOnly]

    def get_serializer_class(self):
        """
        Returns OffersCreateSerializer for Post requests and OffersGetSerializer for Get requests
        """
        if self.request.method == 'POST':
            return OffersCreateSerializer
        return OffersGetSerializer

    def perform_create(self, serializer):
        """
        Saves a new offer instence and automatically assigns the requesting user as the creator.
        """
        serializer.save(user=self.request.user)


class OfferDetailView(generics.RetrieveAPIView):
    """
    API view for a single offer detail.
    """
    permission_classes = [IsAuthenticated]
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    lookup_url_kwarg = 'id'
