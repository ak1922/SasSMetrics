from django import forms
from django.utils.translation import gettext_lazy as _

from apps.billing.models import SubscriptionEvent


class SubscriptionEventForm(forms.ModelForm):
    class Meta:
        model = SubscriptionEvent
        fields = (
            'customer_id',
            'event_type',
            'amount',
            'recorded_at'
        )
        widgets = {
            'customer_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('e.g. cust_stripe_101')
            }),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'recorded_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }
