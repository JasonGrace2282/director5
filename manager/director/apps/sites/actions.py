from collections.abc import Iterator
from typing import Any, cast

from .appserver import Appserver
from .models import Site
from .parser import SiteConfig


def find_pingable_appservers(_site: Site, scope: dict[str, Any]) -> Iterator[str]:
    yield "Pinging appservers"
    appservers = Appserver.list_pingable()
    scope["pingable_appservers"] = appservers
    yield f"Found {len(appservers)} pingable appservers"


def update_docker_service(site: Site, scope: dict[str, Any]) -> Iterator[str]:
    """Create or update a Docker service for a site.

    Expects scope to be populated with ``pingable_appservers``.
    If scope has a :class:`.SiteConfig`, it will use the Docker base image from there.
    """
    if site.availability == "disabled":
        yield from remove_docker_service(site, scope)
        return

    yield "Connecting to appserver to create/update docker service."
    appserver = Appserver.random(scope["pingable_appservers"])
    director_config = cast(SiteConfig | None, scope.get("director_config"))
    data = {
        "pk": site.pk,
        "hosts": site.list_domains(),
        "is_served": site.is_served,
        "type_": site.mode,
        "resource_limits": site.serialize_resource_limits(),
        "docker": {"base": site.docker_image(director_config)},
    }
    appserver.http_request("/api/docker/update-docker-service", method="POST", data=data)
    yield "Created/updated Docker service"


def remove_docker_service(_site: Site, scope: dict[str, Any]) -> Iterator[str]:
    appserver = Appserver.random(scope["pingable_appservers"])
    yield f"Removing Docker service on {appserver}"
    # TODO
    yield "Docker service removed"
