from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'

    def get_page_size(self, request):
        value = request.query_params.get(self.page_size_query_param)
        if value in (None, ''):
            return self.page_size
        try:
            size = int(value)
        except (ValueError, TypeError):
            raise ValidationError({'page_size': 'Enter a positive integer.'})
        if size < 1:
            raise ValidationError({'page_size': 'Enter a positive integer.'})
        return size
