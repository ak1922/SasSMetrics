from django.contrib import admin
from apps.billing.models import SubscriptionEvent


@admin.register(SubscriptionEvent)
class SubscriptionEvent(admin.ModelAdmin):
    list_display = (
        'tenant',
        'event_type',
        'customer_id',
        'amount',
        'recorded_at'
    )

    list_filter = (
        'event_type',
        'recorded_at',
        'tenant'
    )

    search_fields = (
        'customer_id',
        'tenant__username',
        'tenant__company_name'
    )

    ordering = ('-recorded_at',)

    raw_id_fields = ('tenant',)
