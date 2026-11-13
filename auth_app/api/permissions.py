from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsProfileOwnerOrReadOnly(BasePermission):
    """Restrict profile changes to the profile owner."""
    def has_object_permission(self, request, view, obj):
        """Allow safe methods and require ownership for changes."""
        if request.method in SAFE_METHODS:
            return True
        return obj.user_id == request.user.id
