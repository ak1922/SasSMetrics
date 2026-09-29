from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect, render

from .forms import SubscriptionEventForm
from .models import SubscriptionEvent


# Create view
@login_required
def create_subscription_event(request):
    if request.method == 'POST':
        form = SubscriptionEventForm(request.POST)

        if form.is_valid():
            event = form.save(commit=False)
            event.tenant = request.user
            event.save()
            return redirect('index')
    else:
        form = SubscriptionEventForm()

    context = {'form': form}

    return render(request, 'billing/create_event.html', context)


# List
@login_required
def subscription_event_logs(request):

    event_list = SubscriptionEvent.objects.for_tenant(request.user)

    paginator = Paginator(event_list, 25)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        return  render(request, 'billing/transaction_rows.html', {
            'transactions': [],
            'has_more': False
        })

    context = {
        'transactions': page_obj.object_list,
        'has_more': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None
    }

    return render(request, 'billing/transaction_rows.html', context)
