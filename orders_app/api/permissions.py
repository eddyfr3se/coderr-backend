from rest_framework.permissions import BasePermission

from auth_app.models import UserProfile


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and UserProfile.objects.filter(
            user=request.user, type='customer',
        ).exists()


class IsOrderBusiness(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and UserProfile.objects.filter(
            user=request.user, type='business',
        ).exists()

    def has_object_permission(self, request, view, obj):
        return obj.business_user_id == request.user.id
