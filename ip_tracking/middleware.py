from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from ipware import get_client_ip
from django.core.cache import cache
from django.utils import timezone

from .models import RequestLog, BlockedIP


CACHE_TTL = 60 * 60 * 24  # 24 hours

def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _normalize_geo(geo):
    if not isinstance(geo, dict):
        return None, None
    country = (
        geo.get('country_name')
        or geo.get('country')
        or geo.get('countryCode')
        or geo.get('country_code')
    )
    city = geo.get('city') or geo.get('region') or geo.get('state')
    return country, city


def _lookup_geo_with_fallback(ip):
    try:
        import ipapi
    except Exception
        return None

    cache_key = f"geo:{ip}"
    cached = cache.get(cache_key)
    if cached:
        return cached.get("country"), cached.get("city")

    country = city = None
    if ipapi:
        try:
            data = ipapi.location(ip)
            if isinstance(data, dict):
                country = data.get("country_name") or data.get("country")
                city = data.get("city")
        except Exception:
            pass

    if country or city:
        cache.set(cache_key, {"country": country, "city": city}, CACHE_TTL)
    return country, city


class IPLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_ip = _get_client_ip(request)

        if BlockedIP.objects.filter(ip_address=client_ip).exists():
            return HttpResponseForbidden("Forbidden.")

        country = city = None
        geo = getattr(request, 'geolocation', None)
        country, city = _normalize_geo(geo)

        if not country and not city:
            country, city = _lookup_geo_with_fallback(client_ip)

        try:
            RequestLog.objects.create(
                ip_address=client_ip,
                country=country,
                city=city,
                path=request.path,
                method=request.method,
                timestamp=timezone.now()
            )
        except Exception:
            pass
        response = self.get_response(request)