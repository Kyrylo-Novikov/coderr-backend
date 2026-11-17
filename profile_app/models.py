from django.db import models
from auth_app.models import CustomUser


class Profile(models.Model):
    """
    Stores the public profile data of a user.

    A profile is created automatically on registration and is linked
    one-to-one to a CustomUser. Name, email and type stay on the user
    model and are only exposed through the serializer.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/',
                            default='uploads/profile_default.jpg')
    location = models.CharField(max_length=50, blank=True)
    tel = models.CharField(max_length=20, blank=True)
    description = models.CharField(max_length=250, blank=True)
    working_hours = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
