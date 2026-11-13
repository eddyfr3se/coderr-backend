from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import UserProfile
from offers_app.models import Offer, OfferDetail


class OfferCreateAPITests(APITestCase):
    """Test offer create api."""
    def setUp(self):
        """Prepare isolated fixtures for the tests in this class."""
        self.url = reverse('offer-list')
        self.business = self.make_user('business', 'business')
        self.customer = self.make_user('customer', 'customer')
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

    def make_user(self, username, profile_type):
        """Create a test user with the requested role."""
        user = get_user_model().objects.create_user(username=username)
        UserProfile.objects.create(user=user, type=profile_type)
        return user

    def authenticate(self, user):
        """Attach a test user token to subsequent API requests."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_business_creates_offer_with_documented_response(self):
        """Verify that business creates offer with documented response."""
        self.authenticate(self.business)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertSetEqual(set(response.data), {
            'id', 'title', 'description', 'image', 'details',
        })
        offer = Offer.objects.get(pk=response.data['id'])
        self.assertEqual(offer.user, self.business)
        self.assertEqual(offer.details.count(), 3)
        self.assertEqual(len(response.data['details']), 3)
        self.assertEqual(
            {item['id'] for item in response.data['details']},
            set(offer.details.values_list('id', flat=True)),
        )

    def test_anonymous_request_is_rejected(self):
        """Verify that anonymous request is rejected."""
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertFalse(Offer.objects.exists())

    def test_customer_request_is_rejected(self):
        """Verify that customer request is rejected."""
        self.authenticate(self.customer)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Offer.objects.exists())

    def test_user_without_profile_is_rejected(self):
        """Verify that user without profile is rejected."""
        user = get_user_model().objects.create_user(username='without_profile')
        self.authenticate(user)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Offer.objects.exists())

    def test_owner_cannot_be_overridden_in_request(self):
        """Verify that owner cannot be overridden in request."""
        self.authenticate(self.business)
        self.data['user'] = self.customer.pk
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Offer.objects.get().user, self.business)

    def test_invalid_packages_leave_database_unchanged(self):
        """Verify that invalid packages leave database unchanged."""
        self.authenticate(self.business)
        for types in (('basic', 'standard'), ('basic', 'basic', 'premium')):
            with self.subTest(types=types):
                details = [dict(self.data['details'][0], offer_type=t) for t in types]
                data = {**self.data, 'details': details}
                response = self.client.post(self.url, data, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertIn('details', response.data)
                self.assertFalse(Offer.objects.exists())
                self.assertFalse(OfferDetail.objects.exists())


class OfferReadAPITests(APITestCase):
    """Test offer read api."""
    def setUp(self):
        """Prepare isolated fixtures for the tests in this class."""
        owner = get_user_model().objects.create_user(username='read_owner')
        self.offer = Offer.objects.create(user=owner, title='Design', description='Logo')
        self.package = OfferDetail.objects.create(
            offer=self.offer, title='Basic', revisions=-1, delivery_time_in_days=7,
            price='50.00', features=['Logo'], offer_type='basic',
        )
        OfferDetail.objects.create(
            offer=self.offer, title='Premium', revisions=5, delivery_time_in_days=2,
            price='200.00', features=['Logo', 'Flyer'], offer_type='premium',
        )
        self.url = reverse('offer-detail', args=[self.offer.pk])
        self.package_url = reverse('offer-package-detail', args=[self.package.pk])

    def authenticate(self, role):
        """Attach a test user token to subsequent API requests."""
        user = get_user_model().objects.create_user(username='reader_' + role)
        UserProfile.objects.create(user=user, type=role)
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_both_roles_read_foreign_offer(self):
        """Verify that both roles read foreign offer."""
        for role in ('customer', 'business'):
            with self.subTest(role=role):
                self.authenticate(role)
                response = self.client.get(self.url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data['user'], self.offer.user_id)
                self.assertSetEqual(set(response.data), {
                    'id', 'user', 'title', 'image', 'description', 'created_at',
                    'updated_at', 'details', 'min_price', 'min_delivery_time',
                })

    def test_minima_are_calculated_independently_and_links_work(self):
        """Verify that minima are calculated independently and links work."""
        self.authenticate('customer')
        response = self.client.get(self.url)
        self.assertEqual(float(response.data['min_price']), 50.0)
        self.assertEqual(response.data['min_delivery_time'], 2)
        self.assertEqual(len(response.data['details']), 2)
        for detail in response.data['details']:
            self.assertSetEqual(set(detail), {'id', 'url'})
            self.assertTrue(detail['url'].startswith('http://testserver/api/offerdetails/'))
            package = self.client.get(detail['url'])
            self.assertEqual(package.status_code, 200)
            self.assertEqual(package.data['id'], detail['id'])

    def test_package_has_documented_fields(self):
        """Verify that package has documented fields."""
        self.authenticate('business')
        response = self.client.get(self.package_url)
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(set(response.data), {
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type',
        })
        self.assertEqual(response.data['features'], ['Logo'])
        self.assertEqual(response.data['revisions'], -1)

    def test_anonymous_reads_are_rejected(self):
        """Verify that anonymous reads are rejected."""
        for url in (self.url, self.package_url):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 401)

    def test_missing_objects_return_404(self):
        """Verify that missing objects return 404."""
        self.authenticate('customer')
        for name in ('offer-detail', 'offer-package-detail'):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name, args=[0])).status_code, 404)
