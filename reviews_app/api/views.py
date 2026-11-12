from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import UserProfile
from offers_app.models import Offer
from orders_app.api.permissions import IsCustomerUser
from reviews_app.models import Review

from .filters import ReviewFilter
from .permissions import IsReviewAuthor
from .serializers import BaseInfoSerializer, ReviewSerializer, ReviewUpdateSerializer


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        data = Review.objects.aggregate(
            review_count=Count('id'), average_rating=Avg('rating'),
        )
        data['average_rating'] = round(data['average_rating'] or 0, 1)
        data['business_profile_count'] = UserProfile.objects.filter(
            type='business',
        ).count()
        data['offer_count'] = Offer.objects.count()
        return Response(BaseInfoSerializer(data).data)


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
