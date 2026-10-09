from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import TenantUser
from apps.analytics.models import SaaSMetricCache
from apps.billing.models import SubscriptionEvent


class Command(BaseCommand):
    help = 'Aggregates chronological transaction streams into precise metrics dashboards.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        tenants = TenantUser.objects.filter(is_active=True)

        self.stdout.write(f'Starting metrics aggregation for {today}')
        processed_count = 0

        for tenant in tenants:
            events = SubscriptionEvent.objects.for_tenant(tenant).order_by('recorded_at')

            if not events.exists():
                continue

            customer_mrr_map = {}
            churned_customers = {}
            all_historical_customers = set()

            for event in events:
                cust_id = event.customer_id
                all_historical_customers.add(cust_id)
                current_value = customer_mrr_map.get(cust_id, Decimal('0.00'))

                if event.event_type == 'NEW':
                    customer_mrr_map[cust_id] = event.amount
                    churned_customers.discard(cust_id)

                elif event.event_type == 'UPGRADE':
                    customer_mrr_map[cust_id] = current_value + event.amount
                    churned_customers.discard(cust_id)

                elif event.event_type == 'DOWNGRADE':
                    new_val = current_value - event.amount
                    customer_mrr_map[cust_id] = new_val if new_val > 0 else Decimal('0.00')

                elif event.event_type == 'CHURN':
                    customer_mrr_map[cust_id] = Decimal('0.00')
                    churned_customers.add(cust_id)

            active_customer_values = [v for v in customer_mrr_map.values() if v > 0]
            mrr = sum(active_customer_values)
            arr = mrr * 12

            total_customers_count = len(all_historical_customers)

            if total_customers_count > 0:
                churn_rate = (len(churned_customers) / total_customers_count) * 100
            else:
                churn_rate = 0.00

            if len(active_customer_values) > 0:
                avg_contract_value = sum(active_customer_values) / len(active_customer_values)
            else:
                avg_contract_value = Decimal('0.00')

            if churn_rate > 0:
                ltv = avg_contract_value / (Decimal(str(churn_rate)) / Decimal('100.00'))
            else:
                ltv = avg_contract_value * Decimal('24.00')

            ltv = ltv.quantize(Decimal('0.01'))

            SaaSMetricCache.objects.save_daily_metrics(
                tenant_user=tenant,
                target_date=today,
                mrr=mrr,
                arr=arr,
                ltv=ltv,
                churn_rate=churn_rate
            )
            processed_count += 1

        self.stdout.write(self.style.SUCCESS(f'Chronological calculation execution complete for {processed_count} tenants.'))

        return str(processed_count)
