from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import UserProfile
from orders_app.models import Order

from .permissions import IsCustomerUser, IsOrderBusiness
from .serializers import OrderCreateSerializer, OrderSerializer, OrderStatusSerializer


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


class OrderUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializer
    http_method_names = ['patch', 'delete', 'options']

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), IsOrderBusiness()]
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]


class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]
    order_status = 'in_progress'
    count_field = 'order_count'

    def get(self, request, business_user_id):
        get_object_or_404(UserProfile, user_id=business_user_id, type='business')
        count = Order.objects.filter(
            business_user_id=business_user_id, status=self.order_status,
        ).count()
        return Response({self.count_field: count})
