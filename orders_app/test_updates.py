from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import UserProfile
from offers_app.models import Offer

from .api.serializers import OrderSerializer
from .models import Order


class OrderUpdateDeleteAPITests(APITestCase):
    def setUp(self):
        self.customer = self.make_user('buyer', 'customer')
        self.business = self.make_user('seller', 'business')
        self.other_business = self.make_user('other_seller', 'business')
        self.staff = get_user_model().objects.create_user(username='staff', is_staff=True)
        self.order = self.make_order('Website')
        self.other_order = self.make_order('Other order')
        self.offer = Offer.objects.create(user=self.business, title='Source offer')
        self.url = reverse('order-detail', kwargs={'pk': self.order.pk})

    def make_user(self, username, role):
        user = get_user_model().objects.create_user(username=username)
        UserProfile.objects.create(user=user, type=role)
        return user

    def make_order(self, title):
        return Order.objects.create(
            customer_user=self.customer, business_user=self.business,
            title=title, price='180.50', revisions=2, delivery_time_in_days=7,
            features=['Startseite'], offer_type='basic',
        )

    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_provider_can_set_all_documented_statuses(self):
        self.authenticate(self.business)
        for value in ('completed', 'cancelled', 'in_progress'):
            with self.subTest(status=value):
                response = self.client.patch(self.url, {'status': value}, format='json')
                self.assertEqual(response.status_code, 200)
                self.assertSetEqual(set(response.data), set(OrderSerializer.Meta.fields))
                self.assertEqual(response.data['status'], value)
                self.order.refresh_from_db()
                self.assertEqual(self.order.status, value)

    def test_status_update_preserves_agreed_data_and_creation_time(self):
        before = dict(OrderSerializer(self.order).data)
        self.authenticate(self.business)
        response = self.client.patch(self.url, {'status': 'completed'}, format='json')
        self.assertEqual(response.status_code, 200)
        for field, value in before.items():
            if field not in ('status', 'updated_at'):
                self.assertEqual(response.data[field], value)
        self.assertNotEqual(response.data['updated_at'], before['updated_at'])

    def test_customer_foreign_provider_and_staff_cannot_patch(self):
        for user in (self.customer, self.other_business, self.staff):
            with self.subTest(user=user.username):
                self.authenticate(user)
                response = self.client.patch(self.url, {'status': 'completed'})
                self.assertEqual(response.status_code, 403)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'in_progress')

    def test_assigned_user_also_needs_business_profile(self):
        self.business.profile.type = 'customer'
        self.business.profile.save()
        self.authenticate(self.business)
        response = self.client.patch(self.url, {'status': 'completed'})
        self.assertEqual(response.status_code, 403)

    def test_anonymous_patch_and_delete_return_401(self):
        for method in ('patch', 'delete'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.url)
                self.assertEqual(response.status_code, 401)
        self.assertTrue(Order.objects.filter(pk=self.order.pk).exists())

    def test_invalid_status_returns_400_without_changes(self):
        self.authenticate(self.business)
        before = dict(OrderSerializer(self.order).data)
        for value in ('unknown', '', None, 123):
            with self.subTest(status=value):
                response = self.client.patch(self.url, {'status': value}, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertIn('status', response.data)
        self.order.refresh_from_db()
        self.assertEqual(dict(OrderSerializer(self.order).data), before)

    def test_extra_fields_return_400_and_do_not_apply_status(self):
        self.authenticate(self.business)
        for field in ('price', 'customer_user', 'business_user', 'title', 'revisions',
                      'features', 'offer_type', 'delivery_time_in_days', 'id',
                      'created_at', 'updated_at', 'offer_detail_id', 'unknown'):
            with self.subTest(field=field):
                response = self.client.patch(
                    self.url, {'status': 'completed', field: 1}, format='json',
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'in_progress')

    def test_empty_patch_requires_status(self):
        self.authenticate(self.business)
        response = self.client.patch(self.url, {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('status', response.data)

    def test_missing_order_returns_404_for_authorized_users(self):
        missing = reverse('order-detail', kwargs={'pk': 999999})
        self.authenticate(self.business)
        self.assertEqual(self.client.patch(missing, {'status': 'completed'}).status_code, 404)
        self.authenticate(self.staff)
        self.assertEqual(self.client.delete(missing).status_code, 404)

    def test_staff_deletes_only_order_with_empty_204(self):
        self.authenticate(self.staff)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')
        self.assertFalse(Order.objects.filter(pk=self.order.pk).exists())
        self.assertTrue(Order.objects.filter(pk=self.other_order.pk).exists())
        self.assertTrue(Offer.objects.filter(pk=self.offer.pk).exists())
        self.assertTrue(get_user_model().objects.filter(pk=self.customer.pk).exists())
        self.assertTrue(get_user_model().objects.filter(pk=self.business.pk).exists())

    def test_nonstaff_participants_and_foreign_provider_cannot_delete(self):
        for user in (self.customer, self.business, self.other_business):
            with self.subTest(user=user.username):
                self.authenticate(user)
                self.assertEqual(self.client.delete(self.url).status_code, 403)
        self.assertTrue(Order.objects.filter(pk=self.order.pk).exists())

    def test_repeated_staff_deletion_returns_404(self):
        self.authenticate(self.staff)
        self.assertEqual(self.client.delete(self.url).status_code, 204)
        self.assertEqual(self.client.delete(self.url).status_code, 404)

    def test_staff_customer_profile_can_delete(self):
        UserProfile.objects.create(user=self.staff, type='customer')
        self.authenticate(self.staff)
        self.assertEqual(self.client.delete(self.url).status_code, 204)

    def test_get_put_and_post_are_not_enabled(self):
        self.authenticate(self.business)
        for method in ('get', 'put', 'post'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.url)
                self.assertEqual(response.status_code, 405)
