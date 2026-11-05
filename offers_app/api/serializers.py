from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    features = serializers.ListField(child=serializers.CharField())
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0,
        coerce_to_string=False,
    )

    class Meta:
        model = OfferDetail
        fields = (
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type',
        )
        read_only_fields = ('id',)


class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
    image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Offer
        fields = ('id', 'title', 'image', 'description', 'details')
        read_only_fields = ('id',)

    def validate_details(self, details):
        if len(details) != 3:
            raise serializers.ValidationError('Exactly three packages are required.')
        offer_types = {detail['offer_type'] for detail in details}
        if offer_types != {'basic', 'standard', 'premium'}:
            raise serializers.ValidationError(
                'Provide basic, standard and premium exactly once each.',
            )
        return details

    @transaction.atomic
    def create(self, validated_data):
        details = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail in details:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer
