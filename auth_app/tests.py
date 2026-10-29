"""Model checks for user profiles before the API is implemented."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase

from .models import UserProfile


class UserProfileTests(APITestCase):
    """Check profile validation, defaults and user relationships."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='profile_test',
        )

    def test_customer_and_business_are_valid_types(self):
        for user_type in ['customer', 'business']:
            with self.subTest(user_type=user_type):
                profile = UserProfile(user=self.user, type=user_type)
                profile.full_clean()

    def test_invalid_type_is_rejected_by_model_validation(self):
        profile = UserProfile(user=self.user, type='unknown')

        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_optional_fields_can_remain_empty(self):
        profile = UserProfile.objects.create(user=self.user, type='customer')
        profile.refresh_from_db()

        for field in ['location', 'tel', 'description', 'working_hours']:
            self.assertEqual(getattr(profile, field), '')
        self.assertFalse(profile.file)
        self.assertIsNotNone(profile.created_at)
        self.assertEqual(str(profile), self.user.username)

    def test_duplicate_profile_is_rejected_by_model_validation(self):
        UserProfile.objects.create(user=self.user, type='customer')
        duplicate = UserProfile(user=self.user, type='business')

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_deleting_user_also_deletes_profile(self):
        profile = UserProfile.objects.create(user=self.user, type='customer')
        profile_id = profile.pk

        self.user.delete()

        self.assertFalse(UserProfile.objects.filter(pk=profile_id).exists())

    def test_deleting_profile_preserves_user(self):
        profile = UserProfile.objects.create(user=self.user, type='customer')
        user_id = self.user.pk

        profile.delete()

        self.assertTrue(get_user_model().objects.filter(pk=user_id).exists())
