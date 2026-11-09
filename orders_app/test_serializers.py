import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.http import Http404
from django.test import TestCase
from rest_framework.renderers import JSONRenderer

from offers_app.models import Offer, OfferDetail

from .api.serializers import OrderCreateSerializer, OrderSerializer
from .models import Order


class OrderSerializerTests(TestCase):
    def setUp(self):
        self.customer = get_user_model().objects.create_user(username='buyer')
        self.business = get_user_model().objects.create_user(username='seller')
        self.offer = Offer.objects.create(user=self.business, title='Website')
        self.package = OfferDetail.objects.create(
            offer=self.offer, title='Basic Website', revisions=-1,
            delivery_time_in_days=7, price='180.50', features=['Startseite'],
            offer_type='basic',
        )

    def create_order(self, extra=None):
        data = {'offer_detail_id': self.package.pk}
        data.update(extra or {})
        serializer = OrderCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save(customer_user=self.customer)

    def test_creation_copies_package_values_and_assigns_users(self):
        order = self.create_order()
        self.assertEqual(order.customer_user, self.customer)
        self.assertEqual(order.business_user, self.business)
        self.assertEqual(order.title, 'Basic Website')
        self.assertEqual(order.price, Decimal('180.50'))
        self.assertEqual(order.revisions, -1)
        self.assertEqual(order.delivery_time_in_days, 7)
        self.assertEqual(order.features, ['Startseite'])
        self.assertEqual(order.offer_type, 'basic')
        self.assertEqual(order.status, 'in_progress')

    def test_read_only_input_cannot_override_server_values(self):
        order = self.create_order({
            'id': 999, 'customer_user': self.business.pk,
            'business_user': self.customer.pk, 'price': 1,
            'status': 'completed', 'title': 'Fake', 'features': ['Fake'],
        })
        self.assertNotEqual(order.pk, 999)
        self.assertEqual(order.customer_user, self.customer)
        self.assertEqual(order.business_user, self.business)
        self.assertEqual(order.price, Decimal('180.50'))
        self.assertEqual(order.status, 'in_progress')
        self.assertEqual(order.title, self.package.title)
        self.assertEqual(order.features, self.package.features)

    def test_output_has_documented_fields_and_numeric_price(self):
        data = OrderSerializer(self.create_order()).data
        self.assertSetEqual(set(data), {
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at',
        })
        rendered = json.loads(JSONRenderer().render(data))
        self.assertEqual(rendered['price'], 180.5)

    def test_create_output_excludes_input_only_package_id(self):
        serializer = OrderCreateSerializer(data={'offer_detail_id': self.package.pk})
        self.assertTrue(serializer.is_valid())
        serializer.save(customer_user=self.customer)
        self.assertNotIn('offer_detail_id', serializer.data)
        self.assertSetEqual(set(serializer.data), set(OrderSerializer.Meta.fields))

    def test_missing_package_id_is_required(self):
        serializer = OrderCreateSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('offer_detail_id', serializer.errors)
        self.assertEqual(Order.objects.count(), 0)

    def test_malformed_package_ids_are_rejected(self):
        for value in ('abc', 0, -1, 1.5, None):
            with self.subTest(value=value):
                serializer = OrderCreateSerializer(data={'offer_detail_id': value})
                self.assertFalse(serializer.is_valid())
                self.assertIn('offer_detail_id', serializer.errors)
        self.assertEqual(Order.objects.count(), 0)

    def test_nonexistent_package_does_not_create_order(self):
        serializer = OrderCreateSerializer(data={'offer_detail_id': 999999})
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(Http404):
            serializer.save(customer_user=self.customer)
        self.assertEqual(Order.objects.count(), 0)

    def test_saved_values_survive_package_change_and_deletion(self):
        order = self.create_order()
        self.package.price = Decimal('220.00')
        self.package.title = 'Changed'
        self.package.features = ['Changed']
        self.package.save()
        self.offer.delete()
        order.refresh_from_db()
        self.assertEqual(order.price, Decimal('180.50'))
        self.assertEqual(order.title, 'Basic Website')
        self.assertEqual(order.features, ['Startseite'])
