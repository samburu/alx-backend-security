from django.utils import timezone
from ip_tracking.models import RequestLog, BlockedIP
from ipware import get_client_ip
from django.http import HttpResponseForbidden
from django.core.cache import cache
from geoip2.database import Reader
from django.conf import settings

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.geoip_reader = Reader(settings.GEOIP_PATH)

    def __call__(self, request):
        # Get client IP address
        client_ip, _ = get_client_ip(request)
        
        # Check if IP is blacklisted
        if client_ip and BlockedIP.objects.filter(ip_address=client_ip).exists():
            return HttpResponseForbidden("Access denied: Your IP address is blocked.")
        
        # Initialize geolocation data
        country = None
        city = None
        
        if client_ip:
            # Check cache for geolocation data
            cache_key = f"geo_{client_ip}"
            geo_data = cache.get(cache_key)
            
            if not geo_data:
                # Fetch geolocation data if not cached
                try:
                    response = self.geoip_reader.city(client_ip)
                    country = response.country.name
                    city = response.city.name
                    # Cache for 24 hours (86400 seconds)
                    cache.set(cache_key, {'country': country, 'city': city}, timeout=86400)
                except Exception as e:
                    # Log error silently (avoid crashing middleware)
                    print(f"Geolocation error for IP {client_ip}: {str(e)}")
            else:
                country = geo_data.get('country')
                city = geo_data.get('city')
            
            # Log request details
            RequestLog.objects.create(
                ip_address=client_ip,
                timestamp=timezone.now(),
                path=request.path,
                country=country,
                city=city
            )

        # Process the request
        response = self.get_response(request)
        return response

    def __del__(self):
        # Close GeoIP2 reader when middleware is destroyed
        self.geoip_reader.close()