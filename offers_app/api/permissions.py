from rest_framework.permissions import SAFE_METHODS, BasePermission

from auth_app.models import UserProfile


class IsBusinessUser(BasePermission):
    """Allow access only to authenticated business profiles."""
    def has_permission(self, request, view):
        """Check authentication and the business profile role."""
        return request.user.is_authenticated and UserProfile.objects.filter(
            user=request.user, type='business',
        ).exists()


class IsOfferOwnerOrReadOnly(BasePermission):
    """Restrict offer changes to the offer owner."""
    def has_object_permission(self, request, view, obj):
        """Allow safe methods and require ownership for changes."""
        return request.method in SAFE_METHODS or obj.user_id == request.user.id
