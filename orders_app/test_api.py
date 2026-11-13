from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import UserProfile
from offers_app.models import Offer, OfferDetail

from .api.serializers import OrderSerializer
from .models import Order


class OrderListCreateAPITests(APITestCase):
    """Test order list create api."""
    def setUp(self):
        """Prepare isolated fixtures for the tests in this class."""
        self.customer = self.make_user('customer', 'customer')
        self.business = self.make_user('business', 'business')
        self.other_customer = self.make_user('other_customer', 'customer')
        self.other_business = self.make_user('other_business', 'business')
        self.offer = Offer.objects.create(user=self.business, title='Website')
        self.package = OfferDetail.objects.create(
            offer=self.offer, title='Basic Website', revisions=2,
            delivery_time_in_days=7, price='180.50', features=['Startseite'],
            offer_type='basic',
        )
        self.url = reverse('order-list')

    def make_user(self, username, role):
        """Create a test user with the requested role."""
        user = get_user_model().objects.create_user(username=username)
        UserProfile.objects.create(user=user, type=role)
        return user

    def authenticate(self, user):
        """Attach a test user token to subsequent API requests."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def make_order(self, customer, business):
        """Create an order with the requested test values."""
        return Order.objects.create(
            customer_user=customer, business_user=business,
            title='Stored package', revisions=2, delivery_time_in_days=7,
            price='180.50', features=['Startseite'], offer_type='basic',
        )

    def test_customer_can_create_with_documented_response(self):
        """Verify that customer can create with documented response."""
        self.authenticate(self.customer)
        response = self.client.post(
            self.url, {'offer_detail_id': self.package.pk}, format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertSetEqual(set(response.data), set(OrderSerializer.Meta.fields))
        self.assertEqual(response.data['customer_user'], self.customer.pk)
        self.assertEqual(response.data['business_user'], self.business.pk)
        self.assertEqual(response.data['price'], Decimal('180.50'))
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertEqual(Order.objects.count(), 1)

    def test_client_cannot_override_users_price_or_status(self):
        """Verify that client cannot override users price or status."""
        self.authenticate(self.customer)
        response = self.client.post(self.url, {
            'offer_detail_id': self.package.pk, 'customer_user': self.business.pk,
            'business_user': self.other_business.pk, 'price': 1, 'status': 'completed',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        order = Order.objects.get()
        self.assertEqual(order.customer_user, self.customer)
        self.assertEqual(order.business_user, self.business)
        self.assertEqual(order.price, Decimal('180.50'))
        self.assertEqual(order.status, 'in_progress')

    def test_business_and_profileless_staff_cannot_create(self):
        """Verify that business and profileless staff cannot create."""
        staff = get_user_model().objects.create_user(username='staff', is_staff=True)
        for user in (self.business, staff):
            with self.subTest(user=user.username):
                self.authenticate(user)
                response = self.client.post(
                    self.url, {'offer_detail_id': self.package.pk}, format='json',
                )
                self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.count(), 0)

    def test_anonymous_requests_return_401(self):
        """Verify that anonymous requests return 401."""
        for method in ('get', 'post'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.url)
                self.assertEqual(response.status_code, 401)
        self.assertEqual(Order.objects.count(), 0)

    def test_missing_or_malformed_package_ids_return_400(self):
        """Verify that missing or malformed package ids return 400."""
        self.authenticate(self.customer)
        for data in ({}, {'offer_detail_id': 'abc'}, {'offer_detail_id': 0},
                     {'offer_detail_id': 1.5}, {'offer_detail_id': None}):
            with self.subTest(data=data):
                response = self.client.post(self.url, data, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertIn('offer_detail_id', response.data)
        self.assertEqual(Order.objects.count(), 0)

    def test_unknown_package_returns_404(self):
        """Verify that unknown package returns 404."""
        self.authenticate(self.customer)
        response = self.client.post(self.url, {'offer_detail_id': 999999})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Order.objects.count(), 0)

    def test_customer_only_sees_own_orders_as_array(self):
        """Verify that customer only sees own orders as array."""
        own = self.make_order(self.customer, self.business)
        self.make_order(self.other_customer, self.business)
        self.authenticate(self.customer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual([order['id'] for order in response.data], [own.pk])

    def test_provider_only_sees_received_orders(self):
        """Verify that provider only sees received orders."""
        first = self.make_order(self.customer, self.business)
        second = self.make_order(self.other_customer, self.business)
        self.make_order(self.customer, self.other_business)
        self.authenticate(self.business)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([order['id'] for order in response.data], [first.pk, second.pk])

    def test_unrelated_users_and_staff_receive_empty_array(self):
        """Verify that unrelated users and staff receive empty array."""
        self.make_order(self.customer, self.business)
        staff = get_user_model().objects.create_user(username='staff', is_staff=True)
        for user in (self.other_customer, self.other_business, staff):
            with self.subTest(user=user.username):
                self.authenticate(user)
                response = self.client.get(self.url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data, [])

    def test_list_queries_do_not_grow_per_order(self):
        """Verify that list queries do not grow per order."""
        self.authenticate(self.customer)
        self.make_order(self.customer, self.business)
        with self.assertNumQueries(2):
            self.client.get(self.url)
        self.make_order(self.customer, self.business)
        self.make_order(self.customer, self.business)
        with self.assertNumQueries(2):
            self.client.get(self.url)

    def test_created_order_keeps_original_price_in_list(self):
        """Verify that created order keeps original price in list."""
        self.authenticate(self.customer)
        created = self.client.post(self.url, {'offer_detail_id': self.package.pk})
        self.assertEqual(created.status_code, 201)
        self.package.price = Decimal('220.00')
        self.package.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['price'], Decimal('180.50'))

    def test_unsupported_collection_methods_return_405(self):
        """Verify that unsupported collection methods return 405."""
        self.authenticate(self.customer)
        for method in ('patch', 'put', 'delete'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.url, {}, format='json')
                self.assertEqual(response.status_code, 405)
