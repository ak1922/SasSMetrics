from django.db import models
from django.db import transaction


class SaasMetricCacheQuerySet(models.QuerySet):
    def for_tenant(self, tenant_user):
        return self.filter(tenant=tenant_user)

    def recent_records(self, days=30):
        return self.order_by('-calculated_for_data')[:days]


class SaasMetricCacheManager(models.Manager):
    def get_queryset(self) -> SaasMetricCacheQuerySet:
        return SaasMetricCacheQuerySet(self.model, using=self._db)

    def for_tenant(self, tenant_user):
        return self.get_queryset().for_tenant(tenant_user)

    def save_daily_metrics(self, tenant_user, target_date, mrr, arr, ltv, churn_rate):
        with transaction.atomic(using=self._db):
            record, created = self.update_or_create(
                tenant=tenant_user,
                calculated_for_data=target_date,
                defaults={
                    'mrr': mrr,
                    'arr': arr,
                    'ltv': ltv,
                    'churn_rate': churn_rate
                }
            )

            return record
