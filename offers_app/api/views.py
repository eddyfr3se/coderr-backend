from django.db.models import Min
from rest_framework.generics import (
    CreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated

from offers_app.models import Offer, OfferDetail

from .permissions import IsBusinessUser, IsOfferOwnerOrReadOnly
from .serializers import (
    OfferCreateSerializer, OfferDetailSerializer, OfferRetrieveSerializer,
    OfferUpdateSerializer,
)


class OfferCreateView(CreateAPIView):
    serializer_class = OfferCreateSerializer
    permission_classes = [IsAuthenticated, IsBusinessUser]

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
