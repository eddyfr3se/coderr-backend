from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated

from offers_app.models import Offer, OfferDetail

from .filters import OfferFilter
from .permissions import IsBusinessUser, IsOfferOwnerOrReadOnly
from .pagination import OfferPagination
from .serializers import (
    OfferCreateSerializer, OfferDetailSerializer, OfferRetrieveSerializer,
    OfferUpdateSerializer, OfferListSerializer,
)


class OfferListCreateView(ListCreateAPIView):
    """List offers publicly and allow business users to create them."""
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['min_price', 'updated_at']
    ordering = ['id']

    def get_permissions(self):
        """Require a business account for creation and allow public reads."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsBusinessUser()]
        return [AllowAny()]

    def get_serializer_class(self):
        """Choose nested creation input or the offer list output."""
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferListSerializer

    def get_queryset(self):
        """Precompute package minima and preload owners and packages."""
        return Offer.objects.annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days'),
        ).select_related('user').prefetch_related('details').order_by('id')

    def perform_create(self, serializer):
        """Assign the authenticated user as the offer owner."""
        serializer.save(user=self.request.user)


class OfferRetrieveView(RetrieveUpdateDestroyAPIView):
    """Retrieve offers and restrict updates and deletion to owners."""
    permission_classes = [IsAuthenticated, IsOfferOwnerOrReadOnly]
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        """Choose the partial update or detailed read serializer."""
        if self.request.method == 'PATCH':
            return OfferUpdateSerializer
        return OfferRetrieveSerializer

    def get_queryset(self):
        """Load offers with package minima and prefetched packages."""
        return Offer.objects.annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days'),
        ).prefetch_related('details')


class OfferPackageRetrieveView(RetrieveAPIView):
    """Return a package to authenticated users."""
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
