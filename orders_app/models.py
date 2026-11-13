from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from offers_app.models import OfferDetail


class Order(models.Model):
    """Store the agreed package data independently of later offer changes."""
    STATUS_CHOICES = (
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    customer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_orders',
    )
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_orders',
    )
    title = models.CharField(max_length=255)
    revisions = models.IntegerField(validators=[MinValueValidator(-1)])
    delivery_time_in_days = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=8, choices=OfferDetail.OFFER_TYPES)
    status = models.CharField(
        max_length=11, choices=STATUS_CHOICES, default='in_progress',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the title for display in the admin and shell."""
        return self.title
