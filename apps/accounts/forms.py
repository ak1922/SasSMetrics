from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import TenantUser


class TenantUserCreationForm(UserCreationForm):

    company_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text=_('The corporate organization name for data isolation.')
    )

    class Meta(UserCreationForm.Meta):
        model = TenantUser
        fields = UserCreationForm.Meta.fields + ('company_name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name != 'company_name':
                field.widget.attrs['class'] = 'form-control'
