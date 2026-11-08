from django.urls import path

from .views import OfferCreateView, OfferPackageRetrieveView, OfferRetrieveView


urlpatterns = [
    path('offers/', OfferCreateView.as_view(), name='offer-list'),
    path('offers/<int:pk>/', OfferRetrieveView.as_view(), name='offer-detail'),
    path(
        'offerdetails/<int:pk>/', OfferPackageRetrieveView.as_view(),
        name='offer-package-detail',
    ),
]
