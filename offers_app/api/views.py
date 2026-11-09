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
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['min_price', 'updated_at']
    ordering = ['id']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsBusinessUser()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferListSerializer

    def get_queryset(self):
        return Offer.objects.annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days'),
        ).select_related('user').prefetch_related('details').order_by('id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OfferRetrieveView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOfferOwnerOrReadOnly]
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return OfferUpdateSerializer
        return OfferRetrieveSerializer

    def get_queryset(self):
        return Offer.objects.annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days'),
        ).prefetch_related('details')


class OfferPackageRetrieveView(RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
