from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import UserProfile

from .models import Review


class ReviewListCreateTests(APITestCase):
    def setUp(self):
        self.customer = self.make_user('buyer', 'customer')
        self.other = self.make_user('other_buyer', 'customer')
        self.provider = self.make_user('provider', 'business')
        self.url = reverse('review-list')
        self.payload = {
            'business_user': self.provider.pk,
            'rating': 4,
            'description': 'Gute Zusammenarbeit.',
        }

    def make_user(self, username, role):
        user = get_user_model().objects.create_user(username=username)
        UserProfile.objects.create(user=user, type=role)
        return user

    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_customer_creates_review_with_server_assigned_reviewer(self):
        self.authenticate(self.customer)
        response = self.client.post(self.url, {**self.payload, 'reviewer': self.other.pk})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['reviewer'], self.customer.pk)
        self.assertEqual(Review.objects.get().reviewer_id, self.customer.pk)

    def test_duplicate_does_not_overwrite_original(self):
        self.authenticate(self.customer)
        self.assertEqual(self.client.post(self.url, self.payload).status_code, 201)
        response = self.client.post(self.url, {**self.payload, 'rating': 1})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.objects.get().rating, 4)

    def test_anonymous_and_business_creation_permissions(self):
        self.assertEqual(self.client.get(self.url).status_code, 401)
        self.assertEqual(self.client.post(self.url, self.payload).status_code, 401)
        self.authenticate(self.provider)
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertEqual(self.client.post(self.url, self.payload).status_code, 403)

    def test_rejects_invalid_ratings_and_nonbusiness_target(self):
        self.authenticate(self.customer)
        for changes in ({'rating': 0}, {'rating': 6}, {'business_user': self.other.pk}):
            with self.subTest(changes=changes):
                response = self.client.post(self.url, {**self.payload, **changes})
                self.assertEqual(response.status_code, 400)
        self.assertFalse(Review.objects.exists())

    def test_filtering_and_ordering(self):
        self.authenticate(self.provider)
        other_provider = self.make_user('other_provider', 'business')
        first = Review.objects.create(
            business_user=self.provider, reviewer=self.customer,
            rating=2, description='Zwei Sterne.',
        )
        second = Review.objects.create(
            business_user=self.provider, reviewer=self.other,
            rating=5, description='Fünf Sterne.',
        )
        Review.objects.create(
            business_user=other_provider, reviewer=self.customer,
            rating=4, description='Anderer Anbieter.',
        )
        result = self.client.get(self.url, {
            'business_user_id': self.provider.pk, 'ordering': '-rating',
        })
        self.assertEqual(result.status_code, 200)
        self.assertEqual([row['id'] for row in result.data], [second.pk, first.pk])
        result = self.client.get(self.url, {
            'business_user_id': self.provider.pk, 'reviewer_id': self.customer.pk,
        })
        self.assertEqual([row['id'] for row in result.data], [first.pk])
        self.assertEqual(self.client.get(self.url, {'reviewer_id': 'x'}).status_code, 400)

    def create_review_detail(self):
        review = Review.objects.create(reviewer=self.customer, **{
            'business_user': self.provider, 'rating': 4, 'description': 'Original.',
        })
        return review, reverse('review-detail', args=[review.pk])

    def test_author_can_patch_rating_or_description(self):
        review, url = self.create_review_detail()
        self.authenticate(self.customer)
        response = self.client.patch(url, {'rating': 5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['description'], 'Original.')
        self.assertEqual(response.data['reviewer'], self.customer.pk)
        response = self.client.patch(url, {'description': 'Aktualisiert.'})
        self.assertEqual(response.status_code, 200)
        review.refresh_from_db()
        self.assertEqual((review.rating, review.description), (5, 'Aktualisiert.'))

    def test_invalid_patch_preserves_review(self):
        review, url = self.create_review_detail()
        self.authenticate(self.customer)
        for data in ({'rating': 6}, {'rating': 1, 'business_user': self.other.pk},
                     {'reviewer': self.other.pk}, {'unknown': 'value'}):
            with self.subTest(data=data):
                self.assertEqual(self.client.patch(url, data).status_code, 400)
        review.refresh_from_db()
        self.assertEqual((review.rating, review.business_user_id), (4, self.provider.pk))

    def test_other_users_including_staff_cannot_modify_review(self):
        review, url = self.create_review_detail()
        self.other.is_staff = True
        self.other.save(update_fields=['is_staff'])
        for user in (self.provider, self.other):
            with self.subTest(user=user):
                self.authenticate(user)
                self.assertEqual(self.client.patch(url, {'rating': 1}).status_code, 403)
                self.assertEqual(self.client.delete(url).status_code, 403)
        review.refresh_from_db()
        self.assertEqual(review.rating, 4)

    def test_anonymous_mutations_are_rejected(self):
        _, url = self.create_review_detail()
        self.assertEqual(self.client.patch(url, {'rating': 1}).status_code, 401)
        self.assertEqual(self.client.delete(url).status_code, 401)

    def test_author_deletes_only_selected_review(self):
        review, url = self.create_review_detail()
        control = Review.objects.create(
            reviewer=self.other, business_user=self.provider,
            rating=2, description='Kontrollbewertung.',
        )
        self.authenticate(self.customer)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())
        self.assertTrue(Review.objects.filter(pk=control.pk).exists())
        self.assertEqual(self.client.delete(url).status_code, 404)
        self.assertEqual(self.client.patch(url, {'rating': 3}).status_code, 404)
