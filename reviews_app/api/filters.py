from django import forms
from django_filters import rest_framework as filters

from reviews_app.models import Review


class IntegerFilter(filters.Filter):
    """Validate filter values as whole numbers."""
    field_class = forms.IntegerField


class ReviewFilter(filters.FilterSet):
    """Filter reviews by business user and reviewer."""
    business_user_id = IntegerFilter()
    reviewer_id = IntegerFilter()

    class Meta:
        """Define model fields available as filters."""
        model = Review
        fields = ('business_user_id', 'reviewer_id')
