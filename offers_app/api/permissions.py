from rest_framework.permissions import SAFE_METHODS, BasePermission

from auth_app.models import UserProfile


class IsBusinessUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and UserProfile.objects.filter(
            user=request.user, type='business',
        ).exists()


class IsOfferOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.user_id == request.user.id
