from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal, Optional

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import SearchVector, TrigramSimilarity
from django.db.models import QuerySet, Q, F
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, TemplateView
from django_htmx.http import HttpResponseLocation, HttpResponseClientRedirect

from .consumers.site_status import trigger_power_event, trigger_operation_updated_event
from ..users.models import User, RecentSite
from . import tasks
from .forms import CreateSiteForm
from .models import Site, Operation, Database

if TYPE_CHECKING:
    from director.djtypes import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)



class SiteBaseView(LoginRequiredMixin, TemplateView):
    template_name = ""

    def dispatch(self, request, *args, **kwargs):
        site = get_object_or_404(Site.objects.filter_visible(self.request.user), id=self.kwargs["site_id"])
        self.site = site
        RecentSite.objects.update_or_create(user=request.user, site=site)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site"] = self.site
        context["recent_sites"] = [
            recent.site
            for recent in RecentSite.objects
                .filter(user=self.request.user)
                .order_by("-viewed_at")
                .select_related("site")[:5]
        ]
        return context

class SiteDashboard(SiteBaseView):
    template_name = "sites/site_dashboard.html"

    def get(self, request, *args, **kwargs):
        threading.Timer(5, trigger_power_event, args=[self.site, "Online"]).start()
        operation = Operation.objects.filter(site=self.site).first()
        if operation:
            start_simulation(self.site, operation)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["operation"] = Operation.objects.filter(site=self.site).first()
        return context

@login_required
def site_database(request: AuthenticatedHttpRequest, site_id: int) -> HttpResponse:
    site = get_object_or_404(Site.objects.filter_visible(request.user), id=site_id)
    recent_sites = Site.objects.filter_visible(request.user)[:5]  # todo: implement later based on recently accessed sites

    return render(request, "sites/site_database.html", {"site": site, "recent_sites": recent_sites})

class SiteDatabase(SiteBaseView):
    template_name = "sites/site_database.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@dataclass
class FileEntry:
    name: str
    type: Literal["file", "folder", "symlink", "previous_directory"]
    path: str
    size_kb: int = None
    modified: Optional[datetime] = None

@login_required
def site_file_manager(request: AuthenticatedHttpRequest, site_id: int, subpath: str = "/site/home/test/dir/") -> HttpResponse:
    site = get_object_or_404(Site.objects.filter_visible(request.user), id=site_id)
    recent_sites = Site.objects.filter_visible(request.user)[:5]  # todo: implement later based on recently accessed sites

    files = [
        FileEntry(name="index.html", type="file", path="/site/home/test/dir/index.html", size_kb=12, modified=datetime.now()),
        FileEntry(name="input.css", type="file", path="/site/home/test/dir/input.css", size_kb=1024, modified=datetime.now()),
        FileEntry(name="uv", type="folder", path="/site/home/test/dir/uv/", size_kb=12, modified=datetime.now()),
        FileEntry(name="uv", type="symlink", path="/site/test", size_kb=12, modified=datetime.now()),
        FileEntry(name="..", type="previous_directory", path="/site/home/test/dir/", size_kb=12, modified=datetime.now()),

    ]

    if subpath == "/site/home/test/dir/index.html":
        site = get_object_or_404(Site.objects.filter_visible(request.user), id=site_id)
        recent_sites = Site.objects.filter_visible(request.user)[
                       :5]  # todo: implement later based on recently accessed sites
        file = FileEntry(name="index.html", type="file", path="/site/home/test/dir/index.html")

        return render(request, "sites/view_file.html",
                      {"site": site, "recent_sites": recent_sites, "path_list": file.path.rstrip("/").split("/"),
                       "path_back": "/site/home/test/dir", "file": file})


    return render(request, "sites/site_file_manager.html", {"site": site, "recent_sites": recent_sites, "path_list": subpath.rstrip("/").split("/"), "path_back": "/site/home/test/", "files": files})

@login_required
def site_console(request: AuthenticatedHttpRequest, site_id: int) -> HttpResponse:
    site = get_object_or_404(Site.objects.filter_visible(request.user), id=site_id)
    recent_sites = Site.objects.filter_visible(request.user)[:5]  # todo: implement later based on recently accessed sites

    return render(request, "sites/site_console.html", {"site": site, "recent_sites": recent_sites})

@login_required
def site_settings(request: AuthenticatedHttpRequest, site_id: int) -> HttpResponse:
    site = get_object_or_404(Site.objects.filter_visible(request.user), id=site_id)
    recent_sites = Site.objects.filter_visible(request.user)[:5]  # todo: implement later based on recently accessed sites

    return render(request, "sites/site_settings.html", {"site": site, "recent_sites": recent_sites})

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
                    F("sim_name") + F("sim_desc")
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


def simulate_action_progress(site, operation, action, step=0):
    """
    step:
        0 = start action (set started_time)
        1 = complete action successfully
        2 = complete action failed
    """

    if step == 0:
        action.started_time = timezone.localtime()
        action.message = "Action started."
        action.user_message = "Work in progress..."
        action.result = None
        action.save(update_fields=["started_time", "message", "user_message", "result"])

        trigger_operation_updated_event(site)
        # Schedule next step: complete successfully after 5 seconds
        threading.Timer(5, simulate_action_progress, args=[site, operation, action, 1]).start()

    elif step == 1:
        action.result = True
        action.message = "Action completed successfully."
        action.user_message = "Done!"
        action.save(update_fields=["result", "message", "user_message"])

        trigger_operation_updated_event(site)
        # You could chain another step if needed or just finish

    elif step == 2:
        action.result = False
        action.message = "Action failed due to an error."
        action.user_message = "Please try again later."
        action.save(update_fields=["result", "message", "user_message"])

        trigger_operation_updated_event(site)


def start_simulation(site, operation):
    """
    Starts simulating actions in operation sequentially with intervals.
    """
    actions = list(operation.action_set.all())  # or operation.actions.all()

    def run_action(index=0):
        if index >= len(actions):
            return  # done

        action = actions[index]

        # Start action after 0 seconds
        simulate_action_progress(site, operation, action, step=0)

        # Schedule next action after 12 seconds (enough for start + complete)
        threading.Timer(12, run_action, args=[index + 1]).start()

    run_action()
