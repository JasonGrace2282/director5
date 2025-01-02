from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django_htmx.http import HttpResponseLocation

from . import tasks
from .forms import CreateSiteForm
from .models import Operation, Site
from .operations import send_operation_updated_message

if TYPE_CHECKING:
    from director.djtypes import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
def index(request: AuthenticatedHttpRequest) -> HttpResponse:
    sites = Site.objects.filter_visible(request.user)

    return render(request, "sites/index.html", {"sites": sites})


@login_required
def create_site(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CreateSiteForm(request.POST)
        if form.is_valid():
            site = form.save()
            site.users.add(request.user)
            op = Operation.objects.create(site=site, ty="create_site")
            tasks.create_site.delay(op.id)
            send_operation_updated_message(site)

            if site.mode == "static":
                return HttpResponseLocation(reverse("sites:index"))

            return HttpResponseLocation(reverse("marketplace:store"))

        if request.htmx:
            return render(request, "sites/partials/create_form.html", {"form": form})

    else:
        form = CreateSiteForm()

    return render(request, "sites/create.html", {"form": form})
