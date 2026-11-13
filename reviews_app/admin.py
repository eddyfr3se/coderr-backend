from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Manage customer reviews and their business users."""
    list_display = ('id', 'business_user', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating',)
    list_select_related = ('business_user', 'reviewer')
    search_fields = ('business_user__username', 'reviewer__username')
    readonly_fields = ('created_at', 'updated_at')
