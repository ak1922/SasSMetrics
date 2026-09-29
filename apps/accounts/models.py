from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class TenantUser(AbstractUser):
    """Custom User model for independent SaaS organization owner"""

    company_name = models.CharField(
        max_length=150,
        blank=True,
        help_text=_('The name of the SaaS organization.')
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_tenant_user'
        verbose_name = _('Tenant User')
        verbose_name_plural = _('Tenant Users')

    def __str__(self):
        return f"{self.username} - {self.company_name or 'No Company Name'}"
