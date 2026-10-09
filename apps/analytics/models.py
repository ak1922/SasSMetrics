from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from .managers import SaasMetricCacheManager


class SaaSMetricCache(models.Model):

    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cached_metrics',
        help_text=_('The corporate organization tenant owning this pre-calculated metrics row.')
    )

    calculated_for_date = models.DateField(
        help_text=_('The unique tracking date representing this specific metrics snapshot.')
    )

    mrr = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.00)]
    )

    arr = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.00)]
    )

    ltv = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.00)]
    )

    churn_rate = models.FloatField(validators=[MinValueValidator(0.00)])
    updated_at = models.DateTimeField(auto_now=True)

    objects = SaasMetricCacheManager()

    class Meta:
        db_table = 'analytics_saas_metric_cache'
        ordering = ('-calculated_for_date',)
        unique_together = ('tenant', 'calculated_for_data')
        verbose_name = ('SaaS Metric Cache',)
        verbose_name_plural = ('SaaS Metrics Cache',)

    def __str__(self):
        return f'{self.tenant.username} | {self.calculated_for_date} | MRR: ${self.mrr}'

    def clean(self):
        super().clean()

        if self.churn_rate > 100.00:
            raise ValidationError({
                'churn_rate': _('Customer churn rate percentage metrics cannot exceed 100.0%.')
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# Audit Log
class TaskAuditLog(models.Model):

    class Statuses(models.TextChoices):
        RUNNING = 'RUNNING', _('🚧 In Progress')
        SUCCESS = 'SUCCESS', _('🏆 Completed Cleanly')
        FAILED = 'FAILED', _('❌ Execution Failure')

    task_name = models.CharField(
        max_length=255,
        default='apps.analytics.tasks.run_metrics_aggregation'
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=15,
        choices=Statuses.choices,
        default=Statuses.RUNNING,
        db_index=True
    )

    tenants_processed = models.IntegerField(default=0)

    error_traceback = models.TextField(
        null=True,
        blank=True,
        help_text=_('System error context if the state transitions to FAILED.')
    )

    class Meta:
        db_table = 'analytics_task_audit_log'
        ordering = ('-started_at',)
        verbose_name = _('Task Audit Log')
        verbose_name_plural = _('Task Audit Logs')

    def __str__(self):
        return f"{self.task_name} | {self.status} | {self.started_at.strftime('%Y-%m-%d %H:%M')}"
