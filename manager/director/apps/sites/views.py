from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django_htmx.http import HttpResponseLocation

from ..users.models import User
from . import tasks
from .forms import CreateSiteForm
from .models import Site

if TYPE_CHECKING:
    from director.djtypes import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
def index(request: AuthenticatedHttpRequest) -> HttpResponse:
    sites = Site.objects.filter_visible(request.user)

    return render(
        request,
        "sites/index.html",
        {
            "sites": sites,
            "filler_elem_count": [None for _ in range((3 - (len(sites) + 1) % 3) % 3)],
        },
    )


class CreateSiteView(LoginRequiredMixin, CreateView):
    model = Site
    form_class = CreateSiteForm
    success_url = reverse_lazy("sites:index")
    template_name = "sites/create.html"

    def get_template_names(self) -> list[str]:
        if self.request.htmx and self.request.method == "POST":
            return ["sites/create.html.partials/site_details.html"]

        return [self.template_name]

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if not self.request.htmx:
            context["users"] = User.objects.filter(is_student=True)

        return context

    def form_valid(self, form) -> HttpResponse | HttpResponseLocation:
        if (
            self.request.htmx and self.request.htmx.trigger != "site-form"
        ):  # Any HTMX submissions from the form is just for validation, the button handles the actual creating
            try:
                users = self.get_selected_users()
            except ValueError as e:
                return HttpResponseBadRequest(str(e))

            site = form.save(commit=False)
            site.save()
            site.users.set(users)
            self.object = site

            op = site.start_operation("create_site")
            tasks.create_site.delay(op.id)

            # todo: snackbar that the site was created
            return HttpResponseLocation(self.get_success_url())

        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form) -> HttpResponse:
        return self.render_to_response(self.get_context_data(form=form))

    def get_selected_users(self) -> QuerySet[User]:
        try:
            user_ids = list(map(int, self.request.POST.getlist("users")))
        except ValueError as ex:
            raise ValueError("Invalid user IDs passed. Was the POST data malformed?") from ex

        if self.request.user.id not in user_ids:
            user_ids.append(self.request.user.id)

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
