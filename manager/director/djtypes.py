"""A module for more convenient type hinting."""

from django.http import HttpRequest

from director.apps.users.models import User


class AuthenticatedHttpRequest(HttpRequest):
    """A type hint for a :class:`django.http.HttpRequest` with a logged-in user."""

    user: User  # type: ignore[assign]
