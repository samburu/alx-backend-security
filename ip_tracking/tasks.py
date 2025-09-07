from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from ip_tracking.models import RequestLog, SuspiciousIP

# Paths that are considered sensitive
SENSITIVE_PATHS = ["/admin", "/login"]

@shared_task
def detect_anomalies():
    """Detect suspicious IPs based on request logs (last 1 hour)."""
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # Get requests in the last hour
    recent_requests = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    ip_data = {}
    for req in recent_requests:
        ip_data.setdefault(req.ip_address, {"count": 0, "paths": []})
        ip_data[req.ip_address]["count"] += 1
        ip_data[req.ip_address]["paths"].append(req.path)

    for ip, data in ip_data.items():
        reasons = []

        # Rule 1: Too many requests
        if data["count"] > 100:
            reasons.append(f"High volume: {data['count']} requests in last hour")

        # Rule 2: Accessing sensitive endpoints
        for path in data["paths"]:
            if any(path.startswith(s) for s in SENSITIVE_PATHS):
                reasons.append(f"Sensitive path accessed: {path}")

        if reasons:
            SuspiciousIP.objects.create(
                ip_address=ip,
                reason="; ".join(reasons)
            )
