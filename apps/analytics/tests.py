from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from .models import SaaSMetricCache, TaskAuditLog
from .tasks import run_metrics_aggregation
from apps.accounts.models import TenantUser
from apps.billing.models import SubscriptionEvent


class SaaSMetricCacheModelTest(TestCase):
    def setUp(self):
        self.tenant = TenantUser.objects.create_user(
            username='tenant_test_firm',
            password='Pass123$Tenant',
            company_name='Test Metrics LLC'
        )
        self.today = timezone.now().date()

    def test_save_daily_metrics_new_row(self):
        """Verify the manager successfully creates a summary row when none exists for the date."""

        record = SaaSMetricCache.objects.save_daily_metrics(
            tenant_user=self.tenant,
            target_date=self.today,
            mrr=Decimal('5000.00'),
            arr=Decimal('60000.00'),
            ltv=Decimal('15000.00'),
            churn_rate=2.5
        )
        self.assertIsNotNone(record)
        self.assertEqual(record.mrr, Decimal('5000.00'))
        self.assertEqual(SaaSMetricCache.objects.count(), 1)

    def test_save_daily_metric_performs_atomic_upsert(self):
        """Verify that running the execution twice on the same day updates the row instead of duplicating it."""

        SaaSMetricCache.objects.save_daily_metrics(
            tenant_user=self.tenant,
            target_date=self.today,
            mrr=Decimal('5000.00'),
            arr=Decimal('60000.00'),
            ltv=Decimal('15000.00'),
            churn_rate=2.5
        )

        updated_record = SaaSMetricCache.objects.save_daily_metrics(
            tenant_user=self.tenant,
            target_date=self.today,
            mrr=Decimal('5200.00'),
            arr=Decimal('66000.00'),
            ltv=Decimal('16000.00'),
            churn_rate=2.2
        )
        self.assertEqual(updated_record.mrr, Decimal('5500.00'))
        self.assertEqual(SaaSMetricCache.objects.count(), 1)


class SaaSAdvancedAnalyticsTest(TestCase):
    def setUp(self):
        self.tenant = TenantUser.objects.create_user(
            username='metrics_firm',
            password='Metric%123Pass',
            company_name='Beta Saas'
        )
        self.base_time = timezone.now()

    def test_account_lifecycle_changes(self):
        SubscriptionEvent.objects.create(
            tenant=self.tenant,
            customer_id='cust_1001',
            event_type='NEW',
            amount=Decimal('50.00'),
            recorded_at=self.base_time
        )

        SubscriptionEvent.objects.create(
            tenant=self.tenant,
            customer_id='cust_1001',
            event_type='UPGRADE',
            amount=Decimal('30.00'),
            recorded_at=self.base_time + timedelta(days=1)
        )

        SubscriptionEvent.objects.create(
            tenant=self.tenant,
            customer_id='cust_1002',
            event_type='NEW',
            amount=Decimal('100.00'),
            recorded_at=self.base_time + timedelta(days=2)
        )

        SubscriptionEvent.objects.create(
            tenant=self.tenant,
            customer_id='cust_1001',
            event_type='DOWNGRADE',
            amount=Decimal('10.00'),
            recorded_at=self.base_time + timedelta(days=3)
        )

        SubscriptionEvent.objects.create(
            tenant=self.tenant,
            customer_id='cust_1002',
            event_type='CHURN',
            amount=Decimal('0.00'),
            recorded_at=self.base_time + timedelta(days=4)
        )

        result = run_metrics_aggregation()
        self.assertEqual(result, 'Metrics compiled cleanly')

        latest_cache = SaaSMetricCache.objects.for_tenant(self.tenant).first()
        self.assertIsNotNone(latest_cache)
        self.assertEqual(latest_cache.mrr, Decimal('70.00'))
        self.assertEqual(latest_cache.arr, Decimal('840.00'))
        self.assertEqual(latest_cache.churn_rate, 50.0)

    def test_task_auditor_logs_successful_execution_state(self):
        """Verify that running the engine task auto-populates successful TaskAuditLog rows."""
        SubscriptionEvent.objects.create(
            tenant=self.tenant, customer_id='cust_99', event_type='NEW',
            amount=Decimal('10.00'), recorded_at=self.base_time
        )

        self.assertEqual(TaskAuditLog.objects.count(), 0)
        run_metrics_aggregation()

        self.assertEqual(TaskAuditLog.objects.count(), 1)
        log_entry = TaskAuditLog.objects.first()
        self.assertEqual(log_entry.status, 'SUCCESS')
        self.assertEqual(log_entry.tenants_processed, 1)
        self.assertIsNone(log_entry.error_traceback)
