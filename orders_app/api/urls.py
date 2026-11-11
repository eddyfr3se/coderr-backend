from django.urls import path

from .views import OrderCountView, OrderListCreateView, OrderUpdateDeleteView


urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderUpdateDeleteView.as_view(), name='order-detail'),
    path(
        'order-count/<int:business_user_id>/',
        OrderCountView.as_view(),
        name='order-count',
    ),
    path(
        'completed-order-count/<int:business_user_id>/',
        OrderCountView.as_view(
            order_status='completed', count_field='completed_order_count',
        ),
        name='completed-order-count',
    ),
]
