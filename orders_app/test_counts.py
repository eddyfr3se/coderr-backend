from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import UserProfile

from .models import Order


class OrderCountAPITests(APITestCase):
    """Test order count api."""
    def setUp(self):
        """Prepare isolated fixtures for the tests in this class."""
        self.customer = self.make_user('buyer', 'customer')
        self.provider = self.make_user('provider', 'business')
        self.other = self.make_user('other_provider', 'business')

    def make_user(self, username, role):
        """Create a test user with the requested role."""
        user = get_user_model().objects.create_user(username=username)
        UserProfile.objects.create(user=user, type=role)
        return user

    def authenticate(self):
        """Attach a test user token to subsequent API requests."""
        token = Token.objects.create(user=self.customer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def make_order(self, provider, status):
        """Create an order with the requested test values."""
        Order.objects.create(
            customer_user=self.customer, business_user=provider,
            title='Website', revisions=2, delivery_time_in_days=4,
            price='80.00', features=['Startseite'], offer_type='basic',
            status=status,
        )

    def get_count(self, route, user_id):
        """Request the selected order count endpoint for a business user."""
        return self.client.get(reverse(route, args=[user_id]))

    def test_counts_only_target_provider_and_matching_status(self):
        """Verify that counts only target provider and matching status."""
        self.authenticate()
        for status in ('in_progress', 'completed', 'completed', 'cancelled'):
            self.make_order(self.provider, status)
        self.make_order(self.other, 'in_progress')
        self.make_order(self.other, 'completed')
        running = self.get_count('order-count', self.provider.pk)
        completed = self.get_count('completed-order-count', self.provider.pk)
        self.assertEqual(running.status_code, 200)
        self.assertEqual(running.data, {'order_count': 1})
        self.assertEqual(completed.status_code, 200)
        self.assertEqual(completed.data, {'completed_order_count': 2})

    def test_business_without_orders_returns_zero(self):
        """Verify that business without orders returns zero."""
        self.authenticate()
        for route, key in (
            ('order-count', 'order_count'),
            ('completed-order-count', 'completed_order_count'),
        ):
            with self.subTest(route=route):
                response = self.get_count(route, self.provider.pk)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data, {key: 0})

    def test_unknown_or_nonbusiness_user_returns_404(self):
        """Verify that unknown or nonbusiness user returns 404."""
        self.authenticate()
        profileless = get_user_model().objects.create_user(username='no_profile')
        for route in ('order-count', 'completed-order-count'):
            for user_id in (999999, self.customer.pk, profileless.pk):
                with self.subTest(route=route, user_id=user_id):
                    self.assertEqual(self.get_count(route, user_id).status_code, 404)

    def test_authentication_required(self):
        """Verify that authentication required."""
        for route in ('order-count', 'completed-order-count'):
            with self.subTest(route=route):
                self.assertEqual(self.get_count(route, self.provider.pk).status_code, 401)
