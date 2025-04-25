"""A collection of utilities for testing sites."""

import contextlib
from collections.abc import Iterator
from typing import Any, NotRequired, TypedDict

import responses
from django.conf import settings

from ..appserver import Appserver


class MockInfo(TypedDict):
    path: str
    data: dict[str, Any]
    status_code: NotRequired[int]
    method: NotRequired[str]


def _url(path: str) -> str:
    """Return the URL for a given path."""
    app1 = settings.DIRECTOR_APPSERVER_HOSTS[0]
    return f"{Appserver.protocol()}://{app1}{path}"


@contextlib.contextmanager
def mock(*args: MockInfo) -> Iterator[None]:
    with responses.RequestsMock() as rsps:
        rsps.add(
            method="GET",
            url=_url("/ping"),
            json={"message": "pong-mocked-appserver"},
            status=200,
        )

        for info in args:
            rsps.add(
                method=info.get("method", "POST"),
                url=_url(info["path"]),
                json=info["data"],
                status=info.get("status_code", 200),
            )
        yield
