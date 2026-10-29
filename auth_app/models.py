from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Store the additional profile data for a Coderr user."""

    USER_TYPES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    type = models.CharField(max_length=8, choices=USER_TYPES)
    location = models.CharField(max_length=255, blank=True, default='')
    tel = models.CharField(max_length=30, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=255, blank=True, default='')
    file = models.FileField(upload_to='profiles/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
