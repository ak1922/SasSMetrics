from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import SaaSMetricCache
from apps.billing.models import SubscriptionEvent


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Renders the secure, authenticated executive workspace layout shell.
    Enforces multi-tenant data isolation via LoginRequiredMixin.
    """

    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['latest_metrics'] = SaaSMetricCache.objects.filter(
            tenant=self.request.user
        ).first()

        return context


@login_required
def metrics_cards_element_view(request):
    
    latest_metrics = SaaSMetricCache.objects.for_tenant(request.user).first()
    context = {'latest_metrics': latest_metrics}

    return render(request, 'analytics/metrics_cards.html', context)


@login_required
def analytics_tabs_view(request):
    
    target_tab = request.GET.get('tab', 'overview')
    context = {'active_tab': target_tab}

    if target_tab == 'transactions':
        context['transactions'] = SubscriptionEvent.objects.for_tenant(request.user)[:50]

    return render(request, 'analytics/tabs_content.html', context)
