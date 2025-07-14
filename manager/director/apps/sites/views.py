from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import SearchVector, TrigramSimilarity
from django.db.models import QuerySet, Q, F
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django_htmx.http import HttpResponseLocation, HttpResponseClientRedirect

from ..users.models import User
from . import tasks
from .forms import CreateSiteForm
from .models import Site

if TYPE_CHECKING:
    from director.djtypes import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
def index(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == "POST" and request.htmx:
        query = request.POST.get("query", "").strip()

        availability_filter = Q()

        if ("served" in request.POST) ^ ("not_served" in request.POST):
            if "served" in request.POST:
                availability_filter = Q(availability=Site.Availabilities.ENABLED)
            else:
                availability_filter = Q(availability__in=[
                    Site.Availabilities.NOT_SERVED,
                    Site.Availabilities.DISABLED
                ])

        sites = Site.objects.filter(Q(users=request.user), availability_filter)

        if query:
            sites = sites.annotate(
                sim_name=TrigramSimilarity("name", query),
                sim_desc=TrigramSimilarity("description", query)
            ).annotate(
                total_similarity=
                    F("sim_name") + F("sim_desc")  # More weighting towards name in search
            ).filter(
                total_similarity__gt=0.2
            ).order_by("-total_similarity")

        return render(request, "sites/sites.html.partials/sites_list.html", {
            "sites": sites,
            "query": query
        })

    sites = Site.objects.filter_visible(request.user)

    if request.htmx:
        return render(request, "sites/sites.html.partials/sites_list.html", {"sites": sites})

    return render(
        request,
        "sites/sites.html",
        {
            "sites": sites,
        },
    )


@login_required
def create_site_view(request):
    form = CreateSiteForm(request.POST)

    if request.htmx and request.method == "POST":
        template = "sites/create.html.partials/site_details.html"
    else:
        template = "sites/create.html"

    context = {"form": form}
    if not request.htmx:
        context["users"] = User.objects.filter(is_student=True)

    if request.method == "POST":
        if form.is_valid():
            # When site-form makes an HTMX request, it's only for validation
            if request.htmx and request.htmx.trigger != "site-form":
                try:
                    users = _get_selected_users(request)
                except ValueError as e:
                    return HttpResponseBadRequest(str(e))

                site = form.save()
                site.users.set(users)

                op = site.start_operation("create_site")
                tasks.create_site.delay(op.id)

                messages.success(request, "Site created successfully")
                return HttpResponseClientRedirect(reverse("sites:index"))
            else:
                return render(request, template, context)

        return render(request, template, context)

    return render(request, template, context)

def create_site_view_basic_form(request):
    form = CreateSiteForm(request.POST)

    if request.method == "POST":
        if form.is_valid():
            site = form.save()
            users = request.POST.getlist("users")
            if request.user.pk not in users:
                users.append(request.user.pk)

            site.users.set(users)

            op = site.start_operation("create_site")
            tasks.create_site.delay(op.id)

            return redirect("sites:index")

    return render(request, "sites/create_basic.html", {"form": form })


def _get_selected_users(request) -> QuerySet[User]:
    try:
        user_ids = list(map(int, request.POST.getlist("users")))
    except ValueError as ex:
        raise ValueError("Invalid user IDs passed. Was the POST data malformed?") from ex

    if request.user.id not in user_ids:
        user_ids.append(request.user.id)

    users = User.objects.filter(id__in=user_ids)
    if len(users) != len(user_ids):
        raise ValueError(
            "One or more selected users do not exist. Try creating the site with just yourself as a collaborator."
        ) from None

    return users

@login_required
@require_POST
def delete_site(request: AuthenticatedHttpRequest, site_id: int) -> HttpResponse:
    site = get_object_or_404(Site.objects.filter_visible(request.user), id=site_id)
    op = site.start_operation("delete_site")
    tasks.delete_site.delay(op.id)
    return redirect("sites:index")
