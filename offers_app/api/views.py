from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated

from offers_app.models import Offer, OfferDetail

from .pagination import GetOffersPagination
from .permissions import IsBusinessUserOrReadOnly, IsOwner
from .serializers import (
    OfferDetailCreateSerializer,
    OffersCreateSerializer,
    OffersListGetSerializer,
    OffersSingleGetSerializer,
    OfferUpdateSerializer,
)


class OffersListView(generics.ListCreateAPIView):
    """
    API view for listing all offers and creating a new offer.
    """
    permission_classes = [IsAuthenticated, IsBusinessUserOrReadOnly]
    pagination_class = GetOffersPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['min_price', '-updated_at']

    def get_queryset(self):
        """
        Annotates offers with minimum price and delivery time and filters by creator ID, min price, and max delivery time.
        """
        queryset = Offer.objects.annotate(min_price=Min('details__price'),
                                          min_delivery_time=Min('details__delivery_time_in_days'))
        creator_id_param = self.request.query_params.get('creator_id')
        min_price_param = self.request.query_params.get('min_price')
        max_delivery_time_param = self.request.query_params.get(
            'max_delivery_time')
        if creator_id_param:
            queryset = queryset.filter(user_id=creator_id_param)
        if min_price_param:
            queryset = queryset.filter(min_price__gte=min_price_param)
        if max_delivery_time_param:
            queryset = queryset.filter(
                min_delivery_time__lte=max_delivery_time_param)
        return queryset

    def get_serializer_class(self):
        """
        Returns the serializer that matches the request method.
        """
        if self.request.method == 'POST':
            return OffersCreateSerializer
        return OffersListGetSerializer

    def perform_create(self, serializer):
        """
        Saves a new offer and sets the requesting user as its creator.
        """
        serializer.save(user=self.request.user)


class OffersDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a specific offer.
    """
    queryset = Offer.objects.all()
    lookup_url_kwarg = 'id'

    def get_permissions(self):
        """
        Returns the permissions for the request method.
        """
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """
        Returns the serializer that matches the request method.
        """
        if self.request.method == 'PATCH':
            return OfferUpdateSerializer
        return OffersSingleGetSerializer


class DetailsView(generics.RetrieveAPIView):
    """
    API view for retrieving a single offer detail
    """
    permission_classes = [IsAuthenticated]
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailCreateSerializer
    lookup_url_kwarg = 'id'
