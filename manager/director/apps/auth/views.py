from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def login_view(request: HttpRequest) -> HttpResponse:
    return render(request, "auth/login.html")


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("auth:index")
