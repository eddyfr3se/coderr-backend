from django.shortcuts import get_object_or_404
from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Return the stored order terms, participants and timestamps."""
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, coerce_to_string=False,
    )

    class Meta:
        """Define serialized model fields and their write permissions."""
        model = Order
        fields = (
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at',
        )
        read_only_fields = fields


class OrderCreateSerializer(OrderSerializer):
    """Create an order from a selected offer package."""
    offer_detail_id = serializers.IntegerField(write_only=True, min_value=1)

    class Meta(OrderSerializer.Meta):
        """Define serialized model fields and their write permissions."""
        fields = OrderSerializer.Meta.fields + ('offer_detail_id',)

    def create(self, validated_data):
        """Copy the chosen package terms and assign both participants."""
        package = get_object_or_404(
            OfferDetail.objects.select_related('offer'),
            pk=validated_data['offer_detail_id'],
        )
        return Order.objects.create(
            customer_user=validated_data['customer_user'],
            business_user_id=package.offer.user_id, title=package.title,
            revisions=package.revisions, price=package.price,
            delivery_time_in_days=package.delivery_time_in_days,
            features=list(package.features), offer_type=package.offer_type,
        )


class OrderStatusSerializer(OrderSerializer):
    """Accept only the documented order status for updates."""
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)

    class Meta(OrderSerializer.Meta):
        """Define serialized model fields and their write permissions."""
        read_only_fields = tuple(
            field for field in OrderSerializer.Meta.fields if field != 'status'
        )

    def validate(self, attrs):
        """Require status and reject all other input fields."""
        extra_fields = set(self.initial_data) - {'status'}
        if extra_fields:
            raise serializers.ValidationError({
                field: 'Only status may be changed.' for field in extra_fields
            })
        if 'status' not in attrs:
            raise serializers.ValidationError({'status': 'This field is required.'})
        return attrs
