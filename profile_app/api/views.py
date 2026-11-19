from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profile_app.models import Profile

from .permissions import IsProfileOwnerOrReadOnly
from .serializers import ProfileSerializer, ProfilesTypeSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or partially update the profile of a user

    Get is allowed for every authenticated user, PATCH only for the owner.
    The profile is addressed by the id of its user.
    """

    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'user_id'
    lookup_url_kwarg = 'pk'


class ProfilesTypeView(generics.ListAPIView):
    """
    Retrieve a list of profiles depending on the type.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfilesTypeSerializer
    user_type = None

    def get_queryset(self):
        return Profile.objects.filter(user__type=self.user_type)
