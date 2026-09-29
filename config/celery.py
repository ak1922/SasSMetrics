import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'compute-saas-metrics-hourly': {
        'task': 'apps.analytics.tasks.run_metrics_aggregation',
        'schedule': crontab(minute=0),
    }
}
