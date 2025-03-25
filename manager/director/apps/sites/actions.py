from collections.abc import Iterator
from typing import Any

import requests

from .appserver import Appserver
from .models import Site


def raise_by_recoverability(site: Site, response: requests.Response):
    if response.status_code == 200:
        return
    if response.status_code == 422:
        raise RuntimeError(f"Invalid JSON: {response.json()}")
    try:
        content = response.json()
    except requests.exceptions.JSONDecodeError as e:
        raise ValueError(
            f"Appserver {site} returned {response.status_code} and could not be decoded to JSON."
        ) from e

    if content.get("user_error"):
        pass  # TODO: handle this to nicely display reason to user
    response.raise_for_status()


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

    appserver = Appserver.random(scope["pingable_appservers"])
    yield f"Connecting to appserver {appserver} to create/update docker service."

    response = appserver.http_request(
        "/api/docker/update-docker-service",
        method="POST",
        data=site.serialize_for_appserver(),
    )
    raise_by_recoverability(site, response)
    yield "Created/updated Docker service"


def remove_docker_service(_site: Site, scope: dict[str, Any]) -> Iterator[str]:
    appserver = Appserver.random(scope["pingable_appservers"])
    yield f"Removing Docker service on {appserver}"
    # TODO
    yield "Docker service removed"


def build_docker_image(site: Site, scope: dict[str, Any]) -> Iterator[str]:
    appserver = Appserver.random(scope["pingable_appservers"])
    yield f"Connecting to appserver {appserver} to build docker image."
    response = appserver.http_request(
        "/api/docker/image/build",
        method="POST",
        data={"site": site.serialize_for_appserver()},
    )
    raise_by_recoverability(site, response)
    yield "Docker image built"
