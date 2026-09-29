from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import TenantUser


@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'company_name',
        'is_staff',
        'is_active',
        'is_superuser',
        'updated_at'
    )

    list_filter = (
        'is_staff',
        'is_active',
        'is_superuser'
    )

    search_fields = (
        'username',
        'email',
        'company_name'
    )

    fieldsets = UserAdmin.fieldsets + (
        (_('SaaS Multi-Tenant Details'), {'fields': ('company_name',)}),
    )
