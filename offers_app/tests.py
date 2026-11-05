from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import SimpleTestCase, TestCase
from rest_framework.renderers import JSONRenderer

from offers_app.api.serializers import (
    OfferCreateSerializer,
    OfferDetailSerializer,
)
from offers_app.models import Offer, OfferDetail


class OfferDetailSerializerTests(SimpleTestCase):
    def setUp(self):
        self.data = {
            'title': 'Basic Design',
            'revisions': 2,
            'delivery_time_in_days': 5,
            'price': 100,
            'features': ['Logo Design', 'Visitenkarte'],
            'offer_type': 'basic',
        }

    def test_numeric_and_string_prices_are_accepted(self):
        for value in (100, 100.5, '100.50'):
            with self.subTest(value=value):
                serializer = OfferDetailSerializer(
                    data={**self.data, 'price': value},
                )
                self.assertTrue(serializer.is_valid(), serializer.errors)
                self.assertEqual(
                    serializer.validated_data['price'], Decimal(str(value)),
                )

    def test_unlimited_revisions_are_accepted(self):
        serializer = OfferDetailSerializer(
            data={**self.data, 'revisions': -1},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_values_are_rejected(self):
        cases = (
            ('revisions', -2), ('revisions', 1.5),
            ('delivery_time_in_days', 0), ('delivery_time_in_days', 1.5),
            ('price', -1), ('price', 'abc'), ('price', '1.234'),
            ('offer_type', 'other'), ('features', 'Logo'),
            ('features', {'title': 'Logo'}), ('features', [{}]),
        )
        for field, value in cases:
            with self.subTest(field=field, value=value):
                serializer = OfferDetailSerializer(data={**self.data, field: value})
                self.assertFalse(serializer.is_valid())
                self.assertIn(field, serializer.errors)

    def test_missing_package_fields_are_rejected(self):
        for field in self.data:
            with self.subTest(field=field):
                data = self.data.copy()
                data.pop(field)
                serializer = OfferDetailSerializer(data=data)
                self.assertFalse(serializer.is_valid())
                self.assertIn(field, serializer.errors)

    def test_price_is_rendered_as_json_number(self):
        serializer = OfferDetailSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = JSONRenderer().render(serializer.data)
        self.assertIn(b'"price":100.0', result)


class OfferCreateSerializerTests(SimpleTestCase):
    def setUp(self):
        package = {
            'title': 'Design', 'revisions': 2, 'delivery_time_in_days': 5,
            'price': '100.00', 'features': ['Logo Design'],
        }
        self.data = {
            'title': 'Grafikdesign', 'description': 'Design für Unternehmen.',
            'image': None,
            'details': [
                {**package, 'offer_type': kind}
                for kind in ('basic', 'standard', 'premium')
            ],
        }

    def test_three_different_packages_are_accepted_in_any_order(self):
        for details in (self.data['details'], self.data['details'][::-1]):
            with self.subTest(details=details):
                serializer = OfferCreateSerializer(
                    data={**self.data, 'details': details},
                )
                self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_wrong_package_counts_are_rejected(self):
        packages = self.data['details']
        for details in ([], packages[:1], packages[:2], packages + packages[:1]):
            with self.subTest(count=len(details)):
                serializer = OfferCreateSerializer(
                    data={**self.data, 'details': details},
                )
                self.assertFalse(serializer.is_valid())
                self.assertIn('details', serializer.errors)

    def test_duplicate_package_type_is_rejected(self):
        self.data['details'][1]['offer_type'] = 'basic'
        serializer = OfferCreateSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('details', serializer.errors)

    def test_invalid_nested_package_is_rejected(self):
        self.data['details'][1]['delivery_time_in_days'] = 0
        serializer = OfferCreateSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(
            'delivery_time_in_days', serializer.errors['details'][1],
        )

    def test_missing_details_are_rejected(self):
        self.data.pop('details')
        serializer = OfferCreateSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('details', serializer.errors)

    def test_image_can_be_omitted(self):
        self.data.pop('image')
        serializer = OfferCreateSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class OfferCreationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='offer_owner')
        package = {
            'title': 'Design', 'revisions': -1, 'delivery_time_in_days': 5,
            'price': '100.50', 'features': ['Logo'],
        }
        self.data = {
            'title': 'Grafikdesign', 'description': 'Design für Unternehmen.',
            'image': None, 'details': [
                {**package, 'offer_type': kind}
                for kind in ('basic', 'standard', 'premium')
            ],
        }

    def test_offer_and_three_linked_packages_are_saved(self):
        serializer = OfferCreateSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        offer = serializer.save(user=self.user)
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(offer.user, self.user)
        self.assertEqual(offer.details.count(), 3)
        self.assertSetEqual(
            set(offer.details.values_list('offer_type', flat=True)),
            {'basic', 'standard', 'premium'},
        )
        self.assertEqual(offer.details.first().price, Decimal('100.50'))
        self.assertIsNone(serializer.data['image'])
        self.assertTrue(all(detail['id'] for detail in serializer.data['details']))

    def test_client_cannot_choose_owner(self):
        other = get_user_model().objects.create_user(username='other_owner')
        serializer = OfferCreateSerializer(data={**self.data, 'user': other.pk})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        offer = serializer.save(user=self.user)
        self.assertEqual(offer.user, self.user)

    def test_package_failure_rolls_back_entire_offer(self):
        serializer = OfferCreateSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        create_package = OfferDetail.objects.create

        def fail_second_package(**kwargs):
            if OfferDetail.objects.exists():
                raise IntegrityError('Package creation failed')
            return create_package(**kwargs)

        with patch.object(OfferDetail.objects, 'create', fail_second_package):
            with self.assertRaises(IntegrityError):
                serializer.save(user=self.user)
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferDetail.objects.count(), 0)
