from django.urls import path

from .views import ProfilesTypeView, ProfileView

urlpatterns = [
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile-detail'),
    path('profiles/business/', ProfilesTypeView.as_view(user_type='business'),
         name='business-profiles'),
    path('profiles/customer/', ProfilesTypeView.as_view(user_type='customer'),
         name='customer-profiles')
]
