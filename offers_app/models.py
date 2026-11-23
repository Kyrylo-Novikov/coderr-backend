from django.db import models

from auth_app.models import CustomUser


class Offer(models.Model):
    """
    Represents a service offer created by a business user.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    image = models.FileField(upload_to='uploads/', blank=True, null=True)
    description = models.CharField(max_length=350)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    """
    Represents the details of an offer.
    """
    offer = models.ForeignKey(
        Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=100)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    OFFER_TYPE = (('basic', 'basic'), ('standard', 'standard'),
                  ('premium', 'premium'))
    offer_type = models.CharField(max_length=100, choices=OFFER_TYPE)

    def __str__(self):
        return f"Das ist das {self.title} detail."
