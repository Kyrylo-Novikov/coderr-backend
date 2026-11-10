from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    TYPE_CHOICE = (('customer', 'customer'), ('business', 'business'))
    type = models.CharField(choices=TYPE_CHOICE)
    email = models.EmailField(unique=True, blank=False)
