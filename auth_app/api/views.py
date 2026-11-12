from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegistrationSerializer


class RegistrationView(generics.CreateAPIView):
    """
    Handles the user registration process.
    """
    serializer_class = RegistrationSerializer
