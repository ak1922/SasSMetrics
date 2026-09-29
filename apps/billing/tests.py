from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import TenantUser
from apps.billing.models import SubscriptionEvent


class SubscriptionEventModelTest(TestCase):
    def setUp(self):
        self.person_a = TenantUser.objects.create_user(
            username='person_a',
            password='Pear$123Company',
            company_name='Pearl Company'
        )
        self.person_b = TenantUser.objects.create_user(
            username='person_b',
            password='Pear$123Company',
            company_name='KingsFord Dist.'
        )

        SubscriptionEvent.objects.create(
            tenant=self.person_a,
            customer_id='cust_101',
            event_type=SubscriptionEvent.EventTypes.NEW,
            amount=100.00,
            recorded_at=timezone.now()
        )

        SubscriptionEvent.objects.create(
            tenant=self.person_a,
            customer_id='cust_102',
            event_type=SubscriptionEvent.EventTypes.CHURN,
            amount=50.00,
            recorded_at=timezone.now()
        )

        SubscriptionEvent.objects.create(
            tenant=self.person_b,
            customer_id='cust_201',
            event_type=SubscriptionEvent.EventTypes.NEW,
            amount=250.00,
            recorded_at=timezone.now()
        )

    def test_tenant_data_isolation(self):
        person_a_records = SubscriptionEvent.objects.for_tenant(self.person_a)
        person_b_records = SubscriptionEvent.objects.for_tenant(self.person_b)

        self.assertEqual(person_a_records.count(), 2)
        self.assertEqual(person_b_records.count(), 1)

        for record in person_a_records:
            self.assertEqual(record.tenant, self.person_a)

    def test_revenue_and_churn_queryset_filter(self):
        tenant_a_qs = SubscriptionEvent.objects.for_tenant(self.person_a)

        active_revenue = tenant_a_qs.active_revenue_events()
        churn_events = tenant_a_qs.churn_events()

        self.assertEqual(active_revenue.count(), 1)
        self.assertEqual(active_revenue.first().event_type, SubscriptionEvent.EventTypes.NEW)

        self.assertEqual(churn_events.count(), 1)
        self.assertEqual(churn_events.first().event_type, SubscriptionEvent.EventTypes.CHURN)
