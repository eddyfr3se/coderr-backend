"""Regression checks for the documented UTC timestamp format."""

from datetime import datetime
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from auth_app.models import UserProfile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from reviews_app.models import Review


class TimestampResponseTests(APITestCase):
    """Check timestamp output across all four apps without losing UTC accuracy."""

    def setUp(self):
        """Create one customer, provider, offer, package, order and review."""
        self.customer = get_user_model().objects.create_user(username='date_customer')
        self.business = get_user_model().objects.create_user(username='date_business')
        self.profile = UserProfile.objects.create(user=self.customer, type='customer')
        UserProfile.objects.create(user=self.business, type='business')
        self.offer = Offer.objects.create(user=self.business, title='Design')
        OfferDetail.objects.create(
            offer=self.offer, title='Basic', revisions=1,
            delivery_time_in_days=3, price=100, offer_type='basic',
        )
        self.order = Order.objects.create(
            customer_user=self.customer, business_user=self.business,
            title='Basic', revisions=1, delivery_time_in_days=3,
            price=100, offer_type='basic',
        )
        self.review = Review.objects.create(
            business_user=self.business, reviewer=self.customer,
            rating=5, description='Good work.',
        )
        self.client.force_authenticate(self.customer)

    def assert_timestamp_responses(self, timestamp, expected):
        """Check exact API strings and verify that stored precision is preserved."""
        UserProfile.objects.filter(pk=self.profile.pk).update(created_at=timestamp)
        for model, instance in (
            (Offer, self.offer), (Order, self.order), (Review, self.review),
        ):
            model.objects.filter(pk=instance.pk).update(
                created_at=timestamp, updated_at=timestamp,
            )
        requests = (
            ('profile-detail', {'pk': self.customer.pk}, None, ('created_at',)),
            ('customer-profile-list', {}, 'list', ('uploaded_at',)),
            ('offer-list', {}, 'results', ('created_at', 'updated_at')),
            ('offer-detail', {'pk': self.offer.pk}, None, ('created_at', 'updated_at')),
            ('order-list', {}, 'list', ('created_at', 'updated_at')),
            ('review-list', {}, 'list', ('created_at', 'updated_at')),
        )
        for name, kwargs, container, fields in requests:
            with self.subTest(endpoint=name):
                response = self.client.get(reverse(name, kwargs=kwargs))
                self.assertEqual(response.status_code, 200)
                data = response.json()
                if container == 'results':
                    data = data['results'][0]
                elif container == 'list':
                    data = data[0]
                for field in fields:
                    self.assertEqual(data[field], expected)
        response = self.client.patch(
            reverse('profile-detail', kwargs={'pk': self.customer.pk}),
            {'location': 'Berlin'}, format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['created_at'], expected)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.created_at, timestamp)
        self.assertEqual(self.profile.created_at.microsecond, 123456)

    def test_winter_timestamps_use_utc_seconds(self):
        """Convert Berlin winter time to UTC and omit fractional seconds."""
        timestamp = datetime(2026, 1, 15, 12, 0, 0, 123456, tzinfo=ZoneInfo('Europe/Berlin'))
        self.assert_timestamp_responses(timestamp, '2026-01-15T11:00:00Z')

    def test_summer_timestamps_use_utc_seconds(self):
        """Convert Berlin summer time to UTC and omit fractional seconds."""
        timestamp = datetime(2026, 7, 15, 12, 0, 0, 123456, tzinfo=ZoneInfo('Europe/Berlin'))
        self.assert_timestamp_responses(timestamp, '2026-07-15T10:00:00Z')
