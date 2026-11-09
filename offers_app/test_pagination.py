from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail


class OfferPaginationAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='page_provider')
        self.url = reverse('offer-list')
        self.offers = [self.make_offer(number) for number in range(7)]

    def make_offer(self, number):
        offer = Offer.objects.create(
            user=self.user, title=f'Logo {number}', description='Design',
        )
        for kind in ('basic', 'standard', 'premium'):
            OfferDetail.objects.create(
                offer=offer, title=kind, offer_type=kind, price=50 + number,
                revisions=2, delivery_time_in_days=3, features=['Logo'],
            )
        return offer

    def test_custom_size_and_navigation_preserve_all_offers(self):
        response = self.client.get(self.url, {'page_size': 3})
        ids = []
        for expected_size in (3, 3, 1):
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['count'], 7)
            self.assertEqual(len(response.data['results']), expected_size)
            ids.extend(item['id'] for item in response.data['results'])
            if response.data['next']:
                response = self.client.get(response.data['next'])
        self.assertIsNone(response.data['next'])
        self.assertEqual(ids, [offer.pk for offer in self.offers])
        previous = self.client.get(response.data['previous'])
        self.assertEqual(len(previous.data['results']), 3)

    def test_first_page_has_no_previous_link(self):
        response = self.client.get(self.url, {'page_size': 2})
        self.assertIsNone(response.data['previous'])
        self.assertIsNotNone(response.data['next'])

    def test_navigation_keeps_filters_search_ordering_and_size(self):
        params = {
            'creator_id': self.user.pk, 'search': 'Logo', 'min_price': 52,
            'max_delivery_time': 3, 'ordering': '-min_price', 'page_size': 2,
        }
        first = self.client.get(self.url, params).data
        self.assertEqual(first['count'], 5)
        query = parse_qs(urlparse(first['next']).query)
        for key, value in params.items():
            self.assertEqual(query[key], [str(value)])
        second = self.client.get(first['next']).data
        self.assertEqual(second['count'], 5)
        self.assertEqual([item['id'] for item in second['results']],
                         [self.offers[4].pk, self.offers[3].pk])

    def test_page_size_larger_than_count_returns_one_page(self):
        response = self.client.get(self.url, {'page_size': 20})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 7)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_empty_page_size_uses_default_six(self):
        response = self.client.get(self.url, {'page_size': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 6)

    def test_invalid_page_sizes_return_400(self):
        for value in ('abc', '0', '-1', '1.5'):
            with self.subTest(value=value):
                response = self.client.get(self.url, {'page_size': value})
                self.assertEqual(response.status_code, 400)
                self.assertIn('page_size', response.data)

    def test_missing_or_invalid_pages_return_404(self):
        for value in ('abc', '0', '-1', '1.5', '3'):
            with self.subTest(value=value):
                response = self.client.get(self.url, {'page': value})
                self.assertEqual(response.status_code, 404)
                self.assertIn('detail', response.data)

    def test_empty_filtered_list_preserves_pagination_envelope(self):
        response = self.client.get(self.url, {'search': 'No match', 'page_size': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'count': 0, 'next': None, 'previous': None, 'results': [],
        })
