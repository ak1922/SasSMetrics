from django.contrib import admin
from .models import SaaSMetricCache, TaskAuditLog


@admin.register(SaaSMetricCache)
class SaasMetricCacheAdmin(admin.ModelAdmin):
    list_display = (
        'tenant',
        'calculated_for_date',
        'mrr',
        'arr',
        'ltv',
        'churn_rate',
        'updated_at'
    )

    list_filter = (
        'calculated_for_date',
        'tenant',
    )

    search_fields = (
        'tenant__username',
        'tenant__company_name'
    )

    readonly_fields = ('updated_at',)

    raw_id_fields = ('tenant',)


@admin.register(TaskAuditLog)
class TaskAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'task_name',
        'status',
        'started_at',
        'completed_at',
        'tenants_processed',
    )

    list_filter = (
        'status',
        'started_at'
    )

    search_fields = (
        'task_name',
        'error_trace'
    )

    readonly_fields = (
        'task_name',
        'started_at',
        'completed_at',
        'status',
        'tenants_processed',
        'error_traceback'
    )

    def has_add_permission(self, request):
        return False
