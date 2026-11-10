from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from auth_app.models import CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    user_id = serializers.IntegerField(source="id", read_only=True)
    # email = serializers.EmailField(required=True)
    type = serializers.ChoiceField(
        choices=CustomUser.TYPE_CHOICE, write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ["token", "username", "email",
                  "password", "repeated_password", "type", "user_id",]

    def validate(self, values):
        if values["password"] != values["repeated_password"]:
            raise serializers.ValidationError(
                {"password": "passwords do not match"})
        return values

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)

        user.save()
        token = Token.objects.create(user=user)
        user.token = token.key
        return user
