# ip_tracking/views.py
from django.http import JsonResponse
from ratelimit.decorators import ratelimit

# Anonymous users → 5 req/min
@ratelimit(key='ip', rate='5/m', block=True)
def anonymous_sensitive_view(request):
    return JsonResponse({"message": "Anonymous sensitive action allowed."})

# Authenticated users → 10 req/min
@ratelimit(key='user_or_ip', rate='10/m', block=True)
def authenticated_sensitive_view(request):
    return JsonResponse({"message": "Authenticated sensitive action allowed."})
