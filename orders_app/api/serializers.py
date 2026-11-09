from django.shortcuts import get_object_or_404
from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, coerce_to_string=False,
    )

    class Meta:
        model = Order
        fields = (
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at',
        )
        read_only_fields = fields


class OrderCreateSerializer(OrderSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True, min_value=1)

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ('offer_detail_id',)

    def create(self, validated_data):
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
