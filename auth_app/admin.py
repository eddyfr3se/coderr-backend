from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Display and manage user profiles in the Django admin."""

    list_display = ['user', 'type', 'location', 'created_at']
    list_filter = ['type']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    list_select_related = ['user']
