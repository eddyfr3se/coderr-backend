from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Validate package fields and return prices as JSON numbers."""
    features = serializers.ListField(child=serializers.CharField())
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0,
        coerce_to_string=False,
    )

    class Meta:
        """Define serialized model fields and their write permissions."""
        model = OfferDetail
        fields = (
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type',
        )
        read_only_fields = ('id',)


class OfferCreateSerializer(serializers.ModelSerializer):
    """Validate and create an offer with three pricing packages."""
    details = OfferDetailSerializer(many=True)
    image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        """Define serialized model fields and their write permissions."""
        model = Offer
        fields = ('id', 'title', 'image', 'description', 'details')
        read_only_fields = ('id',)

    def validate_details(self, details):
        """Require basic, standard and premium packages exactly once each."""
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
        """Save the offer and all packages in one transaction."""
        details = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail in details:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer


class OfferUpdateSerializer(OfferCreateSerializer):
    """Update an offer and identify existing packages by type."""
    def validate_details(self, details):
        """Require unique types that identify existing packages."""
        types = [detail.get('offer_type') for detail in details]
        if None in types:
            raise serializers.ValidationError('Each package requires offer_type.')
        if len(types) != len(set(types)):
            raise serializers.ValidationError('Package types must not be repeated.')
        existing = [detail.offer_type for detail in self.instance.details.all()]
        if any(existing.count(kind) != 1 for kind in types):
            raise serializers.ValidationError('Package type must identify one existing package.')
        return details

    @transaction.atomic
    def update(self, instance, validated_data):
        """Save offer fields and partial package changes atomically."""
        details = validated_data.pop('details', [])
        instance = super().update(instance, validated_data)
        packages = {detail.offer_type: detail for detail in instance.details.all()}
        for detail in details:
            package = packages[detail['offer_type']]
            OfferDetailSerializer().update(package, detail)
        return instance


class OfferPackageLinkSerializer(serializers.ModelSerializer):
    """Return the identifier and API link for a package."""
    url = serializers.HyperlinkedIdentityField(view_name='offer-package-detail')

    class Meta:
        """Define serialized model fields and their write permissions."""
        model = OfferDetail
        fields = ('id', 'url')
        read_only_fields = fields


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """Return offer details with precomputed package minima."""
    details = OfferPackageLinkSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, coerce_to_string=False,
    )
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        """Define serialized model fields and their write permissions."""
        model = Offer
        fields = (
            'id', 'user', 'title', 'image', 'description', 'created_at',
            'updated_at', 'details', 'min_price', 'min_delivery_time',
        )
        read_only_fields = fields


class OfferUserSerializer(serializers.ModelSerializer):
    """Return the public name fields of an offer owner."""
    class Meta:
        """Define serialized model fields and their write permissions."""
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username')
        read_only_fields = fields


class OfferListSerializer(OfferRetrieveSerializer):
    """Include owner information in each offer list entry."""
    user_details = OfferUserSerializer(source='user', read_only=True)

    class Meta(OfferRetrieveSerializer.Meta):
        """Define serialized model fields and their write permissions."""
        fields = OfferRetrieveSerializer.Meta.fields + ('user_details',)
        read_only_fields = fields
