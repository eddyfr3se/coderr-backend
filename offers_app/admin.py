from django.contrib import admin

from .models import Offer, OfferDetail


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Manage offers and display their owners and timestamps."""
    list_display = ('title', 'user', 'created_at', 'updated_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('user',)


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Manage offer packages, prices and delivery times."""
    list_display = (
        'title', 'offer', 'offer_type', 'price', 'delivery_time_in_days',
    )
    list_filter = ('offer_type',)
    search_fields = ('title', 'offer__title')
    list_select_related = ('offer',)
