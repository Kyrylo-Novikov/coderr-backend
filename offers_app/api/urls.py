from django.urls import path

from .views import DetailsView, OffersDetailView, OffersListView

urlpatterns = [
    path('offers/', OffersListView.as_view(), name='offers-list'),
    path('offers/<int:id>/', OffersDetailView.as_view(), name='offers-detail'),
    path('offerdetails/<int:id>/', DetailsView.as_view(),
         name='offerdetails-detail')
]
