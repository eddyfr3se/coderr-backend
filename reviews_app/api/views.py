from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from orders_app.api.permissions import IsCustomerUser
from reviews_app.models import Review

from .filters import ReviewFilter
from .permissions import IsReviewAuthor
from .serializers import ReviewSerializer, ReviewUpdateSerializer


class ReviewListCreateView(ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['rating', 'updated_at']
    ordering = ['-updated_at', '-id']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class ReviewUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    permission_classes = [IsAuthenticated, IsReviewAuthor]
    http_method_names = ['patch', 'delete', 'options']
