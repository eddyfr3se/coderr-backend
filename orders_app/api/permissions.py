from rest_framework.permissions import BasePermission

from auth_app.models import UserProfile


class IsCustomerUser(BasePermission):
    """Allow access only to authenticated customer profiles."""
    def has_permission(self, request, view):
        """Check authentication and the customer profile role."""
        return request.user.is_authenticated and UserProfile.objects.filter(
            user=request.user, type='customer',
        ).exists()


class IsOrderBusiness(BasePermission):
    """Restrict order changes to the assigned business user."""
    def has_permission(self, request, view):
        """Require an authenticated business profile."""
        return request.user.is_authenticated and UserProfile.objects.filter(
            user=request.user, type='business',
        ).exists()

    def has_object_permission(self, request, view, obj):
        """Check that the requester is the order's assigned business user."""
        return obj.business_user_id == request.user.id
