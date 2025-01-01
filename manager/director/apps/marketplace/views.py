import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from director.djtypes import AuthenticatedHttpRequest

logger = logging.getLogger(__name__)


@login_required
def store(request: AuthenticatedHttpRequest) -> HttpResponse:
    return render(
        request,
        "marketplace/store.html",
    )
