from django.urls import path

from .views import BaseInfoView, ReviewListCreateView, ReviewUpdateDeleteView


urlpatterns = [
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
    path('reviews/', ReviewListCreateView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', ReviewUpdateDeleteView.as_view(), name='review-detail'),
]
