# ip_tracking/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .models import RequestLog, SuspiciousIP

SENSITIVE_PATHS = ["/admin", "/login"]

@shared_task
def detect_anomalies():
    """
    Detect suspicious IP activity:
    - >100 requests in the past hour
    - Accessing sensitive paths
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # 1. Check high-frequency IPs
    ip_counts = (
        RequestLog.objects.filter(timestamp__gte=one_hour_ago)
        .values("ip_address")
        .annotate(count=models.Count("id"))
    )

    for entry in ip_counts:
        if entry["count"] > 100:
            SuspiciousIP.objects.get_or_create(
                ip_address=entry["ip_address"],
                reason="Exceeding 100 requests per hour"
            )

    # 2. Check sensitive paths
    sensitive_logs = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago,
        path__in=SENSITIVE_PATHS
    )
    for log in sensitive_logs:
        SuspiciousIP.objects.get_or_create(
            ip_address=log.ip_address,
            reason=f"Accessed sensitive path {log.path}"
        )

