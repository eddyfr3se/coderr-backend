"""Public registration and login endpoints."""

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import UserProfile

from .permissions import IsProfileOwnerOrReadOnly
from .serializers import (
    BusinessProfileSerializer,
    CustomerProfileSerializer,
    LoginSerializer,
    ProfileDetailSerializer,
    ProfileUpdateSerializer,
    RegistrationSerializer,
)


def get_auth_data(user):
    """Return the documented token and account fields without passwords."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        'token': token.key,
        'username': user.username,
        'email': user.email,
        'user_id': user.pk,
    }


class RegistrationView(APIView):
    """Create a user with its customer or business profile."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """Validate registration data and return the new account token."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(get_auth_data(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticate a username and return its token."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """Validate credentials and return the account token."""
        serializer = LoginSerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response(get_auth_data(user), status=status.HTTP_200_OK)


class ProfileDetailView(RetrieveUpdateAPIView):
    """Allow authenticated profile reads and updates by the owner."""
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    http_method_names = ['get', 'patch', 'head', 'options']
    lookup_field = 'user_id'
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        """Load profiles and their users in a single query."""
        return UserProfile.objects.select_related('user')

    def get_serializer_class(self):
        """Choose the update serializer for PATCH and detail serializer otherwise."""
        if self.request.method == 'PATCH':
            return ProfileUpdateSerializer
        return ProfileDetailSerializer

    def update(self, request, *args, **kwargs):
        """Apply a partial update and return the complete profile."""
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True,
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        output = ProfileDetailSerializer(
            instance, context=self.get_serializer_context(),
        )
        return Response(output.data)


class BusinessProfileListView(ListAPIView):
    """List business profiles with their related user data."""
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessProfileSerializer
    pagination_class = None
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        """Load business profiles ordered by user identifier."""
        return UserProfile.objects.filter(type='business').select_related(
            'user',
        ).order_by('user_id')


class CustomerProfileListView(ListAPIView):
    """List customer profiles with their related user data."""
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerProfileSerializer
    pagination_class = None
    http_method_names = ['get', 'head', 'options']

    def get_queryset(self):
        """Load customer profiles ordered by user identifier."""
        return UserProfile.objects.filter(type='customer').select_related(
            'user',
        ).order_by('user_id')
