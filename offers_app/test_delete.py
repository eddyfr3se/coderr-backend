from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail


class OfferDeleteAPITests(APITestCase):
    """Test offer delete api."""
    def setUp(self):
        """Prepare isolated fixtures for the tests in this class."""
        self.owner = get_user_model().objects.create_user(username='delete_owner')
        self.offer = Offer.objects.create(user=self.owner, title='Design', description='Logo')
        for kind in ('basic', 'standard', 'premium'):
            OfferDetail.objects.create(
                offer=self.offer, title=kind, offer_type=kind, revisions=2,
                delivery_time_in_days=5, price=100, features=['Logo'],
            )
        self.package_ids = list(self.offer.details.values_list('pk', flat=True))
        self.url = reverse('offer-detail', args=[self.offer.pk])

    def authenticate(self, user):
        """Attach a test user token to subsequent API requests."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_owner_deletes_offer_and_packages_only(self):
        """Verify that owner deletes offer and packages only."""
        other_offer = Offer.objects.create(user=self.owner, title='Other', description='Other')
        self.authenticate(self.owner)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')
        self.assertFalse(Offer.objects.filter(pk=self.offer.pk).exists())
        self.assertFalse(OfferDetail.objects.filter(pk__in=self.package_ids).exists())
        self.assertTrue(Offer.objects.filter(pk=other_offer.pk).exists())
        self.assertTrue(get_user_model().objects.filter(pk=self.owner.pk).exists())
        self.assertEqual(self.client.get(self.url).status_code, 404)
        for pk in self.package_ids:
            url = reverse('offer-package-detail', args=[pk])
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_foreign_user_and_staff_cannot_delete(self):
        """Verify that foreign user and staff cannot delete."""
        for staff in (False, True):
            user = get_user_model().objects.create_user(
                username=f'delete_foreign_{staff}', is_staff=staff, is_superuser=staff,
            )
            self.authenticate(user)
            self.assertEqual(self.client.delete(self.url).status_code, 403)
        self.assertTrue(Offer.objects.filter(pk=self.offer.pk).exists())
        self.assertEqual(self.offer.details.count(), 3)

    def test_anonymous_delete_is_rejected(self):
        """Verify that anonymous delete is rejected."""
        self.assertEqual(self.client.delete(self.url).status_code, 401)
        self.assertTrue(Offer.objects.filter(pk=self.offer.pk).exists())
        self.assertEqual(self.offer.details.count(), 3)

    def test_missing_and_repeated_delete_return_404(self):
        """Verify that missing and repeated delete return 404."""
        self.authenticate(self.owner)
        missing = reverse('offer-detail', args=[0])
        self.assertEqual(self.client.delete(missing).status_code, 404)
        self.assertEqual(self.client.delete(self.url).status_code, 204)
        self.assertEqual(self.client.delete(self.url).status_code, 404)
