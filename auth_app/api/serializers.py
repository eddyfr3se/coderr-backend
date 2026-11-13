"""Validate authentication input and serialize profile data."""

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework import serializers

from auth_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    """Define the documented registration fields."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )
    repeated_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )
    type = serializers.ChoiceField(choices=UserProfile.USER_TYPES)

    class Meta:
        """Define serialized model fields and their write permissions."""
        model = get_user_model()
        fields = [
            'username',
            'email',
            'password',
            'repeated_password',
            'type',
        ]

    def validate_email(self, value):
        """Reject email addresses already used by another account."""
        if get_user_model().objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Email already exists.')
        return value

    def validate(self, attrs):
        """Require the password and repeated password to match."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {'repeated_password': 'Passwords do not match.'}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create the user and profile together in one transaction."""
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')
        user = get_user_model().objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, type=user_type)
        return user


class LoginSerializer(serializers.Serializer):
    """Authenticate the documented username and password credentials."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        """Authenticate the credentials and attach the active user."""
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['username'],
            password=attrs['password'],
        )
        if user is None:
            raise serializers.ValidationError('Invalid username or password.')
        attrs['user'] = user
        return attrs


class ProfileDetailSerializer(serializers.ModelSerializer):
    """Return the documented profile detail fields without private data."""

    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        """Define serialized model fields and their write permissions."""
        model = UserProfile
        fields = (
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
        )
        read_only_fields = fields


class BusinessProfileSerializer(ProfileDetailSerializer):
    """Serialize the public fields of business profiles."""
    class Meta:
        """Define serialized model fields and their write permissions."""
        model = UserProfile
        fields = (
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
        )
        read_only_fields = fields


class CustomerProfileSerializer(ProfileDetailSerializer):
    """Serialize customer profiles with their upload timestamp."""
    uploaded_at = serializers.DateTimeField(
        source='created_at', read_only=True,
    )

    class Meta:
        """Define serialized model fields and their write permissions."""
        model = UserProfile
        fields = (
            'user', 'username', 'first_name', 'last_name', 'file',
            'uploaded_at', 'type',
        )
        read_only_fields = fields


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Validate and update the editable user and profile fields."""

    first_name = serializers.CharField(
        source='user.first_name', required=False, allow_blank=True,
        max_length=150,
    )
    last_name = serializers.CharField(
        source='user.last_name', required=False, allow_blank=True,
        max_length=150,
    )
    email = serializers.EmailField(source='user.email', required=False)

    class Meta:
        """Define serialized model fields and their write permissions."""
        model = UserProfile
        fields = (
            'first_name',
            'last_name',
            'location',
            'tel',
            'description',
            'working_hours',
            'email',
            'file',
        )

    def validate_email(self, value):
        """Reject another user's email while allowing the current email."""
        users = get_user_model().objects.filter(email__iexact=value)
        if users.exclude(pk=self.instance.user_id).exists():
            raise serializers.ValidationError('Email already exists.')
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        """Save related user fields and profile fields atomically."""
        user_data = validated_data.pop('user', {})
        for field, value in user_data.items():
            setattr(instance.user, field, value)
        if user_data:
            instance.user.save(update_fields=list(user_data))
        return super().update(instance, validated_data)
