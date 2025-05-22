from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_htmx.http import HttpResponseLocation

from . import tasks
from .forms import CreateSiteForm
from .models import Site

if TYPE_CHECKING:
    from director.djtypes import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)

superuser_required = user_passes_test(lambda u: u.is_superuser)


@login_required
def index(request: AuthenticatedHttpRequest) -> HttpResponse:
    sites = Site.objects.filter_visible(request.user)

    return render(request, "sites/index.html", {"sites": sites})


@login_required
def site_dashboard(request: AuthenticatedHttpRequest, site_id: int) -> HttpResponse:
    site = get_object_or_404(Site.objects.filter_visible(request.user), id=site_id)
    return render(request, "sites/dashboard.html", {"site": site})


@login_required
def create_site(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CreateSiteForm(request.POST)
        if form.is_valid():
            site = form.save()
            site.users.add(request.user)
            op = site.start_operation("create_site")
            tasks.create_site.delay(op.id)

            if site.mode == "static":
                return HttpResponseLocation(reverse("sites:index"))

            return HttpResponseLocation(reverse("marketplace:store"))

        if request.htmx:
            return render(request, "sites/partials/create_form.html", {"form": form})

    else:
        form = CreateSiteForm()

    return render(request, "sites/create.html", {"form": form})


@login_required
@require_POST
def delete_site(request: AuthenticatedHttpRequest, site_id: int) -> HttpResponse:
    site = get_object_or_404(Site.objects.filter_visible(request.user), id=site_id)
    op = site.start_operation("delete_site")
    tasks.delete_site.delay(op.id)
    return redirect("sites:index")


@require_POST
@superuser_required
@login_required
def clear_operations(request: AuthenticatedHttpRequest, site_id: int) -> HttpResponse:
    site = get_object_or_404(Site, id=site_id)
    site.operation_set.all().delete()
    return JsonResponse({})
