import random
from collections.abc import Iterator

import requests

from .appserver import Appserver
from .models import Site
from .operations import UserFacingError


def raise_by_recoverability(site: Site, response: requests.Response):
    if response.status_code == 200:
        return
    if response.status_code == 422:
        raise RuntimeError(f"Invalid JSON: {response.json()}")
    try:
        content = response.json()
    except requests.exceptions.JSONDecodeError as e:
        raise ValueError(
            f"Appserver ({site=}) returned {response.status_code} and could not be decoded to JSON."
        ) from e

    if content.get("user_error") and (explanation := content.get("explanation")):
        description = content.get("description", "An error occurred")
        raise UserFacingError(f"{description}: {explanation}")
    response.raise_for_status()


def update_docker_service(site: Site, appservers: list[Appserver]) -> Iterator[str]:
    """Create or update a Docker service for a site.

    Expects scope to be populated with ``pingable_appservers``.
    If scope has a :class:`.SiteConfig`, it will use the Docker base image from there.
    """
    if site.availability == "disabled":
        yield from remove_docker_service(site, appservers)
        return
    appserver = random.choice(appservers)
    yield f"Connecting to {appserver} to create/update docker service."

    response = appserver.http_request(
        "/api/docker/service/update",
        method="POST",
        data=site.serialize_for_appserver(),
    )
    raise_by_recoverability(site, response)
    yield "Created/updated Docker service"


def build_docker_image(site: Site, appservers: list[Appserver]) -> Iterator[str]:
    appserver = random.choice(appservers)
    yield f"Connecting to appserver {appserver} to build docker image."
    response = appserver.http_request(
        "/api/docker/image/build",
        method="POST",
        data={"site": site.serialize_for_appserver()},
    )
    raise_by_recoverability(site, response)
    yield "Docker image built"


# For the following delete/remove actions, we don't really
# care if they fail - we're just blindly deleting everything


def delete_site_files(site: Site, appservers: list[Appserver]) -> Iterator[str]:
    appserver = random.choice(appservers)
    yield f"Connecting to {appserver} to delete site files."
    appserver.http_request(
        "/api/files/delete-all",
        method="POST",
        data=site.serialize_for_appserver(),
    )
    yield "Site files deleted"


def delete_site_database(site: Site, appservers: list[Appserver]) -> Iterator[str]:
    appserver = random.choice(appservers)
    yield f"Connecting to {appserver} to delete site database."
    appserver.http_request(
        "/api/database/delete",
        method="POST",
        data=site.serialize_for_appserver(),
    )
    yield "Site database deleted"


def remove_docker_service(site: Site, appservers: list[Appserver]) -> Iterator[str]:
    appserver = random.choice(appservers)
    yield f"Removing Docker service on {appserver}"
    appserver.http_request(
        "/api/docker/service/remove",
        method="POST",
        data=site.serialize_for_appserver(),
    )
    yield "Docker service removed"


def remove_docker_image(site: Site, appservers: list[Appserver]) -> Iterator[str]:
    appserver = random.choice(appservers)
    yield f"Removing Docker image on {appserver}"
    appserver.http_request(
        "/api/docker/image/delete",
        method="POST",
        data=site.serialize_for_appserver(),
    )
    yield "Docker image removed"
