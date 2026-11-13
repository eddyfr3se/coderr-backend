from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Offer(models.Model):
    """Store an offer owned by a business user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers',
    )
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to='offers/', blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the title for display in the admin and shell."""
        return self.title


class OfferDetail(models.Model):
    """Store one pricing package belonging to an offer."""
    OFFER_TYPES = (
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='details',
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
    offer_type = models.CharField(max_length=8, choices=OFFER_TYPES)

    def __str__(self):
        """Return the title for display in the admin and shell."""
        return self.title
