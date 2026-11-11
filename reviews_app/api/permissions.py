from rest_framework.permissions import BasePermission


class IsReviewAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.reviewer_id == request.user.pk
