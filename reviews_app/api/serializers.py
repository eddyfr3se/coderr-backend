from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews_app.models import Review


class BaseInfoSerializer(serializers.Serializer):
    """Return public marketplace counts and the average rating."""
    review_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    business_profile_count = serializers.IntegerField(read_only=True)
    offer_count = serializers.IntegerField(read_only=True)


class ReviewSerializer(serializers.ModelSerializer):
    """Validate reviews and prevent duplicate ratings per provider."""
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.filter(profile__type='business'),
    )

    class Meta:
        """Define serialized model fields and their write permissions."""
        model = Review
        fields = (
            'id', 'business_user', 'reviewer', 'rating', 'description',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'reviewer', 'created_at', 'updated_at')

    def create(self, validated_data):
        """Create one review per customer and provider or reject a duplicate."""
        review, created = Review.objects.get_or_create(
            business_user=validated_data['business_user'],
            reviewer=validated_data['reviewer'],
            defaults={
                'rating': validated_data['rating'],
                'description': validated_data['description'],
            },
        )
        if not created:
            raise serializers.ValidationError({
                'business_user': 'You already reviewed this provider.',
            })
        return review


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Limit review updates to rating and description."""
    class Meta(ReviewSerializer.Meta):
        """Define serialized model fields and their write permissions."""
        read_only_fields = (
            'id', 'business_user', 'reviewer', 'created_at', 'updated_at',
        )

    def validate(self, attrs):
        """Reject input fields other than rating and description."""
        extra_fields = set(self.initial_data) - {'rating', 'description'}
        if extra_fields:
            raise serializers.ValidationError({
                field: 'Only rating and description may be changed.'
                for field in sorted(extra_fields)
            })
        return attrs
