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
        )