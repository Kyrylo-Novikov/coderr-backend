from rest_framework import serializers
from profile_app.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializes a profile togehter with the user data from the frontend needs

    first_name, last_name and email are writeble and stored on the related user. All other user fields(is,username,type) are read-only
    """
    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(
        source='user.first_name', allow_blank=True)
    last_name = serializers.CharField(
        source='user.last_name', allow_blank=True)
    email = serializers.EmailField(source='user.email')
    type = serializers.CharField(source='user.type', read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'username', 'first_name',
                  'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'email', 'type', 'created_at']

    def update(self, instance, validated_data):
        """
        Writes the nested user data to the related user, then updates the profile.
        """
        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
        return super().update(instance, validated_data)
