from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import UserProfile
from offers_app.models import Offer

from .models import Review


class BaseInfoTests(APITestCase):
    """Test base info."""
    def make_user(self, username, role):
        """Create a test user with the requested role."""
        user = get_user_model().objects.create_user(username=username)
        UserProfile.objects.create(user=user, type=role)
        return user

    def test_empty_database_is_public_and_returns_zeroes(self):
        """Verify that empty database is public and returns zeroes."""
        response = self.client.get(reverse('base-info'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            'review_count': 0, 'average_rating': 0.0,
            'business_profile_count': 0, 'offer_count': 0,
        })

    def make_reviews(self, provider):
        """Create reviews with the ratings needed for aggregate tests."""
        for number, rating in enumerate((4, 4, 5)):
            customer = self.make_user(f'buyer{number}', 'customer')
            Review.objects.create(
                business_user=provider, reviewer=customer,
                rating=rating, description='Gute Zusammenarbeit.',
            )

    def test_global_counts_and_rounded_average_use_three_queries(self):
        """Verify that global counts and rounded average use three queries."""
        provider = self.make_user('provider', 'business')
        self.make_user('other_provider', 'business')
        get_user_model().objects.create_user(username='without_profile')
        self.make_reviews(provider)
        for number in range(2):
            Offer.objects.create(user=provider, title=f'Offer {number}')
        with self.assertNumQueries(3):
            response = self.client.get(reverse('base-info'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            'review_count': 3, 'average_rating': 4.3,
            'business_profile_count': 2, 'offer_count': 2,
        })

    def test_provider_without_reviews_still_counts(self):
        """Verify that provider without reviews still counts."""
        provider = self.make_user('provider', 'business')
        Offer.objects.create(user=provider, title='Website')
        response = self.client.get(reverse('base-info'))
        self.assertEqual(response.json(), {
            'review_count': 0, 'average_rating': 0.0,
            'business_profile_count': 1, 'offer_count': 1,
        })

    def test_write_methods_are_not_allowed(self):
        """Verify that write methods are not allowed."""
        for method in ('post', 'put', 'patch', 'delete'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(reverse('base-info'))
                self.assertEqual(
                    response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED,
                )
