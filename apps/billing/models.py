from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import SubscriptionEventManager


# Event log model
class SubscriptionEvent(models.Model):
    class EventTypes(models.TextChoices):
        NEW = 'NEW', _('New Sign-up')
        UPGRADE = 'UPGRADE', _('Plan Upgrade')
        DOWNGRADE = 'DOWNGRADE', _('Plan Downgrade')
        CHURN = 'CHURN', _('Plan Cancellation')

    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription_events',
        help_text=_('The corporate organization tenant owning this data partition.')
    )

    customer_id = models.CharField(
        max_length=100,
        db_index=True,
        help_text=_('The unique upstream contract tracking identifier.')
    )

    event_type = models.CharField(
        max_length=10,
        choices=EventTypes.choices,
        help_text=_('The precise business classification of this lifecycle mutation.')
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
        help_text=_('The monthly recurring revenue (MRR) monetary impact of this change.')
    )

    recorded_at = models.DateTimeField(
        db_index=True,
        help_text=_('The timestamp designating when the specific event occurred.')
    )

    objects = SubscriptionEventManager()

    class Meta:
        db_table = 'billing_subscription_event'
        ordering = ('-recorded_at',)
        verbose_name = _('Subscription Event')
        verbose_name_plural = _('Subscription Events')

    def __str__(self):
        return f'{self.tenant.username} | {self.event_type} | {self.customer_id} | ${self.amount}'

    def clean(self):
        super().clean()

        if self.event_type == 'CHURN' and self.amount != 0:
            raise ValidationError({
                'amount': _('A cancellation (CHURN) event type must carry an MRR value delta of exactly $0.00.')
            })

        if self.event_type == 'DOWNGRADE' and self.amount <= 0:
            raise ValidationError({
                'amount': _('A plan downgrade event must retain an active, non-zero contractual value. For total loss, map as CHURN.')
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
