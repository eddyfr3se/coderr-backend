from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.filter(profile__type='business'),
    )

    class Meta:
        model = Review
        fields = (
            'id', 'business_user', 'reviewer', 'rating', 'description',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'reviewer', 'created_at', 'updated_at')

    def create(self, validated_data):
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
    class Meta(ReviewSerializer.Meta):
        read_only_fields = (
            'id', 'business_user', 'reviewer', 'created_at', 'updated_at',
        )

    def validate(self, attrs):
        extra_fields = set(self.initial_data) - {'rating', 'description'}
        if extra_fields:
            raise serializers.ValidationError({
                field: 'Only rating and description may be changed.'
                for field in sorted(extra_fields)
            })
        return attrs
