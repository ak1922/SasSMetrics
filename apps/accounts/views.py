from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import TenantUserCreationForm


# Register user
class RegisterTenantView(CreateView):

    form_class = TenantUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('account:login')
