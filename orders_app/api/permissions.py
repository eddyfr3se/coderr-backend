from rest_framework.permissions import BasePermission

from auth_app.models import UserProfile


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and UserProfile.objects.filter(
            user=request.user, type='customer',
        ).exists()
