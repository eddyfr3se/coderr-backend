from django import forms
from django_filters import rest_framework as filters

from reviews_app.models import Review


class IntegerFilter(filters.Filter):
    field_class = forms.IntegerField


class ReviewFilter(filters.FilterSet):
    business_user_id = IntegerFilter()
    reviewer_id = IntegerFilter()

    class Meta:
        model = Review
        fields = ('business_user_id', 'reviewer_id')
