from django.db import models


# Custom queryset
class SubscriptionEventQuerySet(models.QuerySet):
    def for_tenant(self, tenant_user):
        """Strictly isolates raw transaction metrics to the active organization."""
        return self.filter(tenant=tenant_user)

    def active_revenue_events(self):
        """Filters events that contribute directly to recurring subscription values."""
        return self.exclude(event_type='CHURN')

    def churn_events(self):
        """Filters transaction events representing complete customer attrition."""
        return self.filter(event_type='CHURN')


# Custom manager
class SubscriptionEventManager(models.Manager):
    def get_queryset(self) -> SubscriptionEventQuerySet:
        return SubscriptionEventQuerySet(self.model, using=self._db)

    def for_tenant(self, tenant_user):
        return self.get_queryset().for_tenant(tenant_user)

    def active_revenue_events(self):
        return self.get_queryset().active_revenue_events()

    def churn_events(self):
        return self.get_queryset().churn_events()
