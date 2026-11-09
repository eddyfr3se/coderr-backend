from django.db.models import Q
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from orders_app.models import Order

from .permissions import IsCustomerUser
from .serializers import OrderCreateSerializer, OrderSerializer


class OrderListCreateView(ListCreateAPIView):
    pagination_class = None

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user),
        ).order_by('id')

    def perform_create(self, serializer):
        serializer.save(customer_user=self.request.user)
