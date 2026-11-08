from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from offers_app.api.serializers import OfferCreateSerializer, OfferUpdateSerializer
from offers_app.models import OfferDetail


class OfferUpdateAPITests(APITestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username='update_owner')
        package = {
            'title': 'Design', 'revisions': 2, 'delivery_time_in_days': 5,
            'price': '100.00', 'features': ['Logo'],
        }
        serializer = OfferCreateSerializer(data={
            'title': 'Design', 'description': 'Original description', 'details': [
                {**package, 'offer_type': kind}
                for kind in ('basic', 'standard', 'premium')
            ],
        })
        serializer.is_valid(raise_exception=True)
        self.offer = serializer.save(user=self.owner)
        self.url = reverse('offer-detail', args=[self.offer.pk])

    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_title_only_preserves_other_fields_and_packages(self):
        self.authenticate(self.owner)
        before = list(self.offer.details.values())
        response = self.client.patch(self.url, {'title': 'New title'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertSetEqual(set(response.data), {
            'id', 'title', 'image', 'description', 'details',
        })
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, 'New title')
        self.assertEqual(self.offer.description, 'Original description')
        self.assertEqual(list(self.offer.details.values()), before)
        self.assertEqual(len(response.data['details']), 3)

    def test_partial_package_update_preserves_ids_and_other_values(self):
        self.authenticate(self.owner)
        before = list(self.offer.details.order_by('pk').values())
        data = {'details': [{'offer_type': 'basic', 'price': '120.00'}]}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        after = list(self.offer.details.order_by('pk').values())
        self.assertEqual(float(after[0]['price']), 120)
        after[0]['price'] = before[0]['price']
        self.assertEqual(after, before)
        self.assertEqual(float(response.data['details'][0]['price']), 120)
        self.assertEqual(len(response.data['details']), 3)

    def test_foreign_user_and_staff_cannot_update(self):
        for staff in (False, True):
            user = get_user_model().objects.create_user(
                username=f'foreign_{staff}', is_staff=staff, is_superuser=staff,
            )
            self.authenticate(user)
            response = self.client.patch(self.url, {'title': 'Forbidden'}, format='json')
            self.assertEqual(response.status_code, 403)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, 'Design')

    def test_anonymous_and_missing_offer(self):
        self.assertEqual(self.client.patch(self.url, {}, format='json').status_code, 401)
        self.authenticate(self.owner)
        missing = reverse('offer-detail', args=[0])
        self.assertEqual(self.client.patch(missing, {}, format='json').status_code, 404)

    def test_invalid_packages_do_not_change_offer(self):
        self.authenticate(self.owner)
        cases = [
            [{'price': 120}], [{'offer_type': 'other'}],
            [{'offer_type': 'basic'}, {'offer_type': 'basic'}],
            [{'offer_type': 'basic', 'delivery_time_in_days': 0}],
        ]
        for details in cases:
            with self.subTest(details=details):
                data = {'title': 'Invalid change', 'details': details}
                response = self.client.patch(self.url, data, format='json')
                self.assertEqual(response.status_code, 400)
                self.offer.refresh_from_db()
                self.assertEqual(self.offer.title, 'Design')

    def test_user_and_package_ids_cannot_be_overridden(self):
        self.authenticate(self.owner)
        package = self.offer.details.get(offer_type='basic')
        data = {'user': 999, 'details': [{'offer_type': 'basic', 'id': 999}]}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.user_id, self.owner.pk)
        self.assertEqual(self.offer.details.get(offer_type='basic').pk, package.pk)

    def test_update_failure_rolls_back_offer_and_packages(self):
        before = list(self.offer.details.order_by('pk').values())
        serializer = OfferUpdateSerializer(self.offer, data={
            'title': 'Changed', 'details': [
                {'offer_type': 'basic', 'price': 120},
                {'offer_type': 'premium', 'price': 200},
            ],
        }, partial=True)
        serializer.is_valid(raise_exception=True)
        with patch.object(OfferDetail, 'save', autospec=True, side_effect=fail_premium):
            with self.assertRaises(IntegrityError):
                serializer.save()
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, 'Design')
        self.assertEqual(list(self.offer.details.order_by('pk').values()), before)


original_package_save = OfferDetail.save


def fail_premium(instance, *args, **kwargs):
    if instance.offer_type == 'premium':
        raise IntegrityError('Package update failed')
    return original_package_save(instance, *args, **kwargs)
