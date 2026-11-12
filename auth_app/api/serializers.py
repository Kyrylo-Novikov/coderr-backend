from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from auth_app.models import CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Validate registration data, with hashing the password, and creates an auth token after a successful registration
    """
    repeated_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    user_id = serializers.IntegerField(source="id", read_only=True)
    type = serializers.ChoiceField(
        choices=CustomUser.TYPE_CHOICE, write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ["token",
                  "username",
                  "email",
                  "password",
                  "repeated_password",
                  "type",
                  "user_id"]

    def validate(self, values):
        """
        Validates that password and repeated_password match.
        """
        if values["password"] != values["repeated_password"]:
            raise serializers.ValidationError(
                {"password": "passwords do not match"})
        return values

    def create(self, validated_data):
        """
        Creates a user, hashes the password, and generates an auth token after a successful registration
        """
        validated_data.pop('repeated_password')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        token, created = Token.objects.get_or_create(user=user)
        user.token = token.key
        return user


class LoginSerializer(serializers.Serializer):
    """
    Validate login data, hashing the password back to the raw password, and returns an auth token, username, email and the id after success.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)

    def validate(self, value):
        """
        Compares the provided credentials against the user DB to authenticate
        """
        username = value.get('username')
        password = value.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError(
                "Invalid credentials.")
        token, created = Token.objects.get_or_create(user=user)
        return {
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id
        }
