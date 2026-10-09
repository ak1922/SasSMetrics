import os
import traceback
from celery import shared_task
from django.core.mail import send_mail
from django.core.management import call_command
from django.utils import timezone

from .models import TaskAuditLog


@shared_task
def run_metrics_aggregation():
    audit_log = TaskAuditLog.objects.create(status='RUNNING')

    try:
        processed_output = call_command('compute_metrics')

        audit_log.status = 'SUCCESS'
        audit_log.tenants_processed = int(processed_output) if processed_output else 0
        audit_log.completed_at = timezone.now()
        audit_log.save()
        return 'Metrics compiled cleanly'
    except Exception as e:
        error_context = traceback.format_exc()

        audit_log.status = 'FAILED'
        audit_log.error_traceback = error_context
        audit_log.completed_at = timezone.now()
        audit_log.save()

        admin_email = os.getenv('ADMIN_NOTIFICATION_EMAIL', 'admin.barocay.com')

        send_mail(
            subject=f"🚨 CRITICAL SYSTEM FAILURE: SaaS Metrics Engine ({timezone.now().strftime('%Y-%m-%d')})",
            message=(
                f"The background task 'run_metrics_aggregation' crashed inside the active pod.\n\n"
                f"Timestamp: {audit_log.started_at}\n"
                f"Log Record Reference ID: {audit_log.id}\n\n"
                f"Exception Stack Trace Traceback Context:\n{error_context}"
            ),
            from_email='monitoring-engine@barocay.com',
            recipient_list=[admin_email],
            fail_silently=True
        )

        raise e
