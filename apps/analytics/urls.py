from django.urls import path
from .views import DashboardView, metrics_cards_element_view, analytics_tabs_view


app_name = 'analytics'


urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('fragments/metrics/', metrics_cards_element_view, name='metrics_cards'),
    path('fragments/tabs/', analytics_tabs_view, name='tabs'),
]
