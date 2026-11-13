from rest_framework.permissions import BasePermission


class IsReviewAuthor(BasePermission):
    """Restrict review changes to the original reviewer."""
    def has_object_permission(self, request, view, obj):
        """Check that the requester created the review."""
        return obj.reviewer_id == request.user.pk
