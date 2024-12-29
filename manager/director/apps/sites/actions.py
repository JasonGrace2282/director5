from collections.abc import Iterator
from typing import Any

from .appserver import Appserver
from .models import Site


def find_pingable_appservers(_site: Site, scope: dict[str, Any]) -> Iterator[str]:
    yield "Pinging appservers"
    appservers = Appserver.list_pingable()
    scope["pingable_appservers"] = appservers


def update_docker_service(site: Site, scope: dict[str, Any]) -> Iterator[str]:
    if site.availability == "disabled":
        yield from remove_docker_service(site, scope)
        return
    appserver = Appserver.random(scope["pingable_appservers"])
    data = {
        "pk": site.pk,
        "hosts": site.list_domains(),
        "is_served": site.is_served,
    }
    appserver.http_request("/api/docker/update-docker-service", method="POST", data=data)


def remove_docker_service(site: Site, scope: dict[str, Any]) -> Iterator[str]:
    appserver = Appserver.random(scope["pingable_appservers"])
    yield f"Removing Docker service on {appserver}"
    # TODO
    yield "Docker service removed"
