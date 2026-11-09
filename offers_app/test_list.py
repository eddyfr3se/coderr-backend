from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail


class OfferListAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='list_provider', first_name='Mara', last_name='Muster',
        )
        self.url = reverse('offer-list')

    def make_offer(self, title):
        offer = Offer.objects.create(user=self.user, title=title, description='Design')
        for kind, price, days in (
            ('basic', 50, 7), ('standard', 100, 5), ('premium', 200, 2),
        ):
            OfferDetail.objects.create(
                offer=offer, title=kind, offer_type=kind, price=price,
                revisions=2, delivery_time_in_days=days, features=['Logo'],
            )
        return offer

    def test_anonymous_list_has_documented_fields_and_provider(self):
        offer = self.make_offer('Logo')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(set(response.data), {'count', 'next', 'previous', 'results'})
        item = response.data['results'][0]
        self.assertSetEqual(set(item), {
            'id', 'user', 'title', 'image', 'description', 'created_at',
            'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details',
        })
        self.assertEqual(item['id'], offer.pk)
        self.assertEqual(item['user_details'], {
            'first_name': 'Mara', 'last_name': 'Muster', 'username': 'list_provider',
        })

    def test_minima_and_package_links(self):
        offer = self.make_offer('Logo')
        item = self.client.get(self.url).data['results'][0]
        self.assertEqual(float(item['min_price']), 50)
        self.assertEqual(item['min_delivery_time'], 2)
        self.assertEqual(len(item['details']), 3)
        for detail in item['details']:
            self.assertSetEqual(set(detail), {'id', 'url'})
            self.assertIn(detail['id'], offer.details.values_list('pk', flat=True))
            self.assertTrue(detail['url'].endswith(f"/offerdetails/{detail['id']}/"))

    def test_empty_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'count': 0, 'next': None, 'previous': None, 'results': [],
        })

    def test_pagination_uses_six_items_and_follows_next_link(self):
        for number in range(7):
            self.make_offer(str(number))
        first = self.client.get(self.url).data
        self.assertEqual(first['count'], 7)
        self.assertEqual(len(first['results']), 6)
        second = self.client.get(first['next']).data
        self.assertEqual(len(second['results']), 1)
        self.assertIsNone(second['next'])
        ids = [item['id'] for item in first['results'] + second['results']]
        self.assertEqual(len(set(ids)), 7)

    def test_list_queries_do_not_grow_per_offer(self):
        self.make_offer('One')
        with self.assertNumQueries(3):
            self.client.get(self.url)
        self.make_offer('Two')
        self.make_offer('Three')
        with self.assertNumQueries(3):
            self.client.get(self.url)

    def test_creator_filter_excludes_other_providers(self):
        own = self.make_offer('Own')
        other_user = get_user_model().objects.create_user(username='other_provider')
        other = self.make_offer('Other')
        other.user = other_user
        other.save()
        response = self.client.get(self.url, {'creator_id': self.user.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual([item['id'] for item in response.data['results']], [own.pk])

    def test_unknown_creator_returns_empty_list(self):
        self.make_offer('Existing')
        response = self.client.get(self.url, {'creator_id': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])

    def test_empty_creator_leaves_list_unfiltered(self):
        self.make_offer('Existing')
        response = self.client.get(self.url, {'creator_id': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_invalid_creator_returns_400(self):
        for value in ('abc', '1.5'):
            with self.subTest(value=value):
                response = self.client.get(self.url, {'creator_id': value})
                self.assertEqual(response.status_code, 400)
                self.assertIn('creator_id', response.data)

    def test_min_price_filters_cheapest_package_inclusively(self):
        cheap = self.make_offer('Cheap')
        expensive = self.make_offer('Expensive')
        expensive.details.filter(offer_type='basic').update(price='100.50')
        expensive.details.filter(offer_type='standard').update(price='150.00')
        response = self.client.get(self.url, {'min_price': '100.50'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data['results']], [expensive.pk])
        self.assertEqual(float(response.data['results'][0]['min_price']), 100.5)
        self.assertEqual(cheap.details.count(), 3)

    def test_max_delivery_time_filters_shortest_time_inclusively(self):
        fast = self.make_offer('Fast')
        slow = self.make_offer('Slow')
        slow.details.update(delivery_time_in_days=6)
        response = self.client.get(self.url, {'max_delivery_time': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data['results']], [fast.pk])
        self.assertEqual(response.data['results'][0]['min_delivery_time'], 2)
        self.assertEqual(len(response.data['results'][0]['details']), 3)

    def test_price_and_delivery_filters_combine_with_creator(self):
        match = self.make_offer('Match')
        cheap = self.make_offer('Cheap')
        cheap.details.filter(offer_type='basic').update(price=10)
        slow = self.make_offer('Slow')
        slow.details.update(delivery_time_in_days=9)
        params = {'creator_id': self.user.pk, 'min_price': 50, 'max_delivery_time': 2}
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], match.pk)

    def test_empty_numeric_filters_are_ignored(self):
        self.make_offer('Existing')
        response = self.client.get(self.url, {'min_price': '', 'max_delivery_time': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_invalid_numeric_filters_return_400(self):
        cases = [('min_price', 'abc'), ('min_price', 'NaN'),
                 ('min_price', 'Infinity'), ('max_delivery_time', 'abc'),
                 ('max_delivery_time', '1.5')]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                response = self.client.get(self.url, {field: value})
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)

    def test_numeric_filters_without_matches_return_empty_results(self):
        self.make_offer('Existing')
        for params in ({'min_price': 999}, {'max_delivery_time': 1}):
            with self.subTest(params=params):
                response = self.client.get(self.url, params)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['results'], [])

    def test_search_matches_title_or_description_case_insensitively(self):
        title_match = self.make_offer('Logo Design')
        description_match = self.make_offer('Branding')
        description_match.description = 'Ein neues Logo'
        description_match.save()
        self.make_offer('Website')
        response = self.client.get(self.url, {'search': 'LOGO'})
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(
            {item['id'] for item in response.data['results']},
            {title_match.pk, description_match.pk},
        )

    def test_search_without_match_returns_empty_list(self):
        self.make_offer('Logo')
        response = self.client.get(self.url, {'search': 'Photography'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])

    def test_price_ordering_in_both_directions(self):
        expensive = self.make_offer('Expensive')
        expensive.details.update(price=200)
        cheap = self.make_offer('Cheap')
        for ordering, expected in (
            ('min_price', [cheap.pk, expensive.pk]),
            ('-min_price', [expensive.pk, cheap.pk]),
        ):
            with self.subTest(ordering=ordering):
                response = self.client.get(self.url, {'ordering': ordering})
                self.assertEqual(response.status_code, 200)
                self.assertEqual([item['id'] for item in response.data['results']], expected)

    def test_updated_at_ordering_in_both_directions(self):
        older = self.make_offer('Older')
        newer = self.make_offer('Newer')
        Offer.objects.filter(pk=older.pk).update(updated_at='2026-01-01T12:00:00Z')
        Offer.objects.filter(pk=newer.pk).update(updated_at='2026-02-01T12:00:00Z')
        for ordering, expected in (
            ('updated_at', [older.pk, newer.pk]),
            ('-updated_at', [newer.pk, older.pk]),
        ):
            with self.subTest(ordering=ordering):
                response = self.client.get(self.url, {'ordering': ordering})
                self.assertEqual(response.status_code, 200)
                self.assertEqual([item['id'] for item in response.data['results']], expected)

    def test_search_numeric_filters_and_ordering_work_together(self):
        cheap = self.make_offer('Logo Basic')
        expensive = self.make_offer('Logo Premium')
        expensive.details.update(price=200)
        self.make_offer('Website')
        params = {
            'search': 'logo', 'creator_id': self.user.pk, 'min_price': 50,
            'max_delivery_time': 2, 'ordering': '-min_price',
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(
            [item['id'] for item in response.data['results']], [expensive.pk, cheap.pk],
        )

    def test_empty_search_and_ordering_use_default_list(self):
        first = self.make_offer('First')
        second = self.make_offer('Second')
        response = self.client.get(self.url, {'search': '', 'ordering': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item['id'] for item in response.data['results']], [first.pk, second.pk],
        )
