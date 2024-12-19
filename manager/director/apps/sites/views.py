from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CreateSiteForm
from .models import Site

if TYPE_CHECKING:
    from django.http import HttpResponse

    from director.djtypes import AuthenticatedHttpRequest


@login_required
def index(request: AuthenticatedHttpRequest) -> HttpResponse:
    sites = Site.objects.filter_visible(request.user)
    return render(request, "sites/index.html", {"sites": sites})


@login_required
def create_site(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CreateSiteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("sites:index")
    else:
        form = CreateSiteForm()
    return render(request, "sites/create.html", {"form": form})
