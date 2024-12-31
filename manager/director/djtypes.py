"""A module for more convenient type hinting."""

from django.http import HttpRequest as HttpRequestBase
from django_htmx.middleware import HtmxDetails

from director.apps.users.models import User


class HTMXRequest(HttpRequestBase):
    htmx: HtmxDetails


class AuthenticatedHttpRequest(HTMXRequest):
    """A type hint for a :class:`django.http.HttpRequest` with a logged-in user."""

    user: User  # type: ignore[assign]
