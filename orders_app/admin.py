from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer_user', 'business_user', 'price', 'status')
    list_filter = ('status', 'offer_type')
    search_fields = ('title', 'customer_user__username', 'business_user__username')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('customer_user', 'business_user')
