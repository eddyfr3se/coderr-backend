from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from auth_app.models import UserProfile


class Command(BaseCommand):
    """Create fictional guest accounts for local development."""
    help = 'Create the two fictional accounts for local frontend guest login.'

    @transaction.atomic
    def handle(self, *args, **options):
        """Create demo accounts only when debug mode is enabled."""
        if not settings.DEBUG:
            raise CommandError('Demo accounts require DJANGO_DEBUG=True.')
        self.create_account('coderr_demo_customer', 'customer')
        self.create_account('coderr_demo_business', 'business')

    def create_account(self, username, role):
        """Create a demo user and profile without changing existing users."""
        user, created = get_user_model().objects.get_or_create(
            username=username, defaults={'email': f'{username}@coderr.example'},
        )
        if not created:
            self.stdout.write(f'{username} already exists and was left unchanged.')
            return
        user.set_password('Coderr-demo-local-2026!')
        user.save(update_fields=['password'])
        UserProfile.objects.create(user=user, type=role)
        self.stdout.write(f'Created {username}.')
