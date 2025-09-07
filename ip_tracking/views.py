from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit
from django.views.decorators.csrf import csrf_exempt

def get_rate(group, request):
    return '10/m' if request.user.is_authenticated else '5/m'

@csrf_exempt
@ratelimit(key='ip', rate=get_rate, method='POST', group='login', block=True)
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse("Login successful")
        else:
            return HttpResponse("Invalid credentials", status=401)
    return HttpResponse("Please submit a POST request with username and password")