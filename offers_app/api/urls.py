from django.urls import path

from .vievs import OffersView, OfferDetailView

urlpatterns = [
    path('offers/', OffersView.as_view(), name='offers-list'),
    path('offerdetails/<int:id>/', OfferDetailView.as_view(),
         name='offerdetails-detail')
]
