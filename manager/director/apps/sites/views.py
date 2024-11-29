from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Site

if TYPE_CHECKING:
    from director.djtypes import AuthenticatedHttpRequest
    from django.http import HttpResponse


@login_required
def index(request: AuthenticatedHttpRequest) -> HttpResponse:
    sites = Site.objects.filter_visible(request.user)
    return render(request, "sites/index.html", {"sites": sites})
