from django.utils.deprecation import MiddlewareMixin
from ipware import get_client_ip

from .models import RequestLog


class IPLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip, _ = get_client_ip(request)
        if ip is None:
            ip = "0.0.0.0"
        # Log the IP address, timestamp, and request path
        RequestLog.objects.create(ip_address=ip, path=request.path)