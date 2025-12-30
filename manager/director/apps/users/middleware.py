from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django_htmx.http import HttpResponseClientRedirect


class RequireGuidelinesMiddleware:
    """Middleware that checks if the user has accepted the guidelines. If not, redirects them to users:accept_guidelines"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if getattr(view_func, "_skip_guidelines_middleware", False):
            return None

        if request.user.is_authenticated and not request.user.accepted_guidelines:
            return redirect("users:accept_guidelines")

        return None

class BanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.is_currently_banned and not request.path in (reverse("users:banned"), reverse("auth:logout")):
            return redirect("users:banned")

        return self.get_response(request)
