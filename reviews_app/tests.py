from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Review


class ReviewModelTests(TestCase):
    def setUp(self):
        users = get_user_model().objects
        self.reviewer = users.create_user(username='reviewer')
        self.provider = users.create_user(username='provider')
        self.other_provider = users.create_user(username='other_provider')

    def create_review(self, provider, rating=4):
        return Review.objects.create(
            reviewer=self.reviewer, business_user=provider,
            rating=rating, description='Gute Zusammenarbeit.',
        )

    def test_same_customer_can_review_different_providers(self):
        self.create_review(self.provider, 1)
        self.create_review(self.other_provider, 5)
        self.assertEqual(self.reviewer.written_reviews.count(), 2)

    def test_database_rejects_duplicate_review(self):
        self.create_review(self.provider)
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.create_review(self.provider)

    def test_database_rejects_rating_outside_range(self):
        for rating in (0, 6):
            with self.subTest(rating=rating):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    self.create_review(self.provider, rating)
