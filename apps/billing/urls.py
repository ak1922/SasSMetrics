from django.urls import path
from .views import create_subscription_event, subscription_event_logs


app_name = 'billing'


urlpatterns = [
    path('event/new/', create_subscription_event, name='create_event'),
    path('events/logs/', subscription_event_logs, name='event_log'),
]
