from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from offers_app.models import Offer, OfferDetail

from .models import Order


class OrderModelTests(TestCase):
    """Test order model."""
    def setUp(self):
        """Prepare isolated fixtures for the tests in this class."""
        self.customer = get_user_model().objects.create_user(username='order_customer')
        self.business = get_user_model().objects.create_user(username='order_business')
        self.offer = Offer.objects.create(user=self.business, title='Website')
        self.package = OfferDetail.objects.create(
            offer=self.offer, title='Basic Website', revisions=2,
            delivery_time_in_days=7, price='180.00', features=['Startseite'],
            offer_type='basic',
        )

    def make_order(self):
        """Create an order with the requested test values."""
        return Order.objects.create(
            customer_user=self.customer, business_user=self.business,
            title=self.package.title, revisions=self.package.revisions,
            delivery_time_in_days=self.package.delivery_time_in_days,
            price=self.package.price, features=list(self.package.features),
            offer_type=self.package.offer_type,
        )

    def test_default_status_timestamps_and_user_relations(self):
        """Verify that default status timestamps and user relations."""
        order = self.make_order()
        order.full_clean()
        self.assertEqual(order.status, 'in_progress')
        self.assertIsNotNone(order.created_at)
        self.assertIsNotNone(order.updated_at)
        self.assertEqual(self.customer.customer_orders.get(), order)
        self.assertEqual(self.business.business_orders.get(), order)
        self.assertEqual(str(order), 'Basic Website')

    def test_stored_package_data_survives_source_changes(self):
        """Verify that stored package data survives source changes."""
        order = self.make_order()
        self.package.title = 'Changed package'
        self.package.price = Decimal('220.00')
        self.package.features = ['Changed feature']
        self.package.save()
        order.refresh_from_db()
        self.assertEqual(order.title, 'Basic Website')
        self.assertEqual(order.price, Decimal('180.00'))
        self.assertEqual(order.features, ['Startseite'])

    def test_deleting_offer_does_not_delete_order(self):
        """Verify that deleting offer does not delete order."""
        order = self.make_order()
        self.offer.delete()
        order.refresh_from_db()
        self.assertFalse(OfferDetail.objects.filter(pk=self.package.pk).exists())
        self.assertEqual(order.price, Decimal('180.00'))
        self.assertEqual(order.business_user, self.business)

    def test_invalid_values_fail_model_validation(self):
        """Verify that invalid values fail model validation."""
        for field, value in (
            ('price', -1), ('delivery_time_in_days', 0), ('revisions', -2),
            ('offer_type', 'unknown'), ('status', 'unknown'),
        ):
            with self.subTest(field=field):
                order = self.make_order()
                setattr(order, field, value)
                with self.assertRaises(ValidationError) as error:
                    order.full_clean()
                self.assertIn(field, error.exception.message_dict)

    def test_unlimited_revisions_and_documented_statuses_are_valid(self):
        """Verify that unlimited revisions and documented statuses are valid."""
        order = self.make_order()
        order.revisions = -1
        for status in ('in_progress', 'completed', 'cancelled'):
            with self.subTest(status=status):
                order.status = status
                order.full_clean()

    def test_feature_defaults_do_not_share_a_list(self):
        """Verify that feature defaults do not share a list."""
        first = Order()
        second = Order()
        first.features.append('Startseite')
        self.assertEqual(second.features, [])
