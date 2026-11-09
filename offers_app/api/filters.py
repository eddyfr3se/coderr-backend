from django import forms
from django_filters import rest_framework as filters

from offers_app.models import Offer


class IntegerFilter(filters.Filter):
    field_class = forms.IntegerField


class OfferFilter(filters.FilterSet):
    creator_id = IntegerFilter(field_name='user_id')
    min_price = filters.NumberFilter(field_name='min_price', lookup_expr='gte')
    max_delivery_time = IntegerFilter(
        field_name='min_delivery_time', lookup_expr='lte',
    )

    class Meta:
        model = Offer
        fields = ('creator_id', 'min_price', 'max_delivery_time')
