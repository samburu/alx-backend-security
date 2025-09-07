from django.urls import path
from . import views

urlpatterns = [
    path("anon-action/", views.anonymous_sensitive_view, name="anon_action"),
    path("auth-action/", views.authenticated_sensitive_view, name="auth_action"),
]