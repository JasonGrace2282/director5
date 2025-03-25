import contextlib
import shutil
import traceback
from pathlib import Path
from typing import Any

import docker
import docker.errors
from fastapi import APIRouter, HTTPException

from . import services
from .schema import ContainerLimits, ExceptionInfo, SiteInfo

router = APIRouter()

TEMPLATE_DIR = Path(__file__).parent / "templates"


@router.post(
    "/image/build",
    responses={
        "500": {"model": ExceptionInfo},
    },
)
def build_image(
    site: SiteInfo,
    resource_limits: ContainerLimits | None = None,
) -> dict[str, Any]:
    client = docker.from_env()

    site_dir = site.directory_path()
    dockerfile_path = site_dir / "Dockerfile"
    # make sure a valid dockerfile always exists
    if not dockerfile_path.exists():
        default_dockerfile = TEMPLATE_DIR / "Dockerfile"
        shutil.copy(default_dockerfile, dockerfile_path)

    # caching or storing intermediate images takes up a
    # ton of space.
    try:
        _image, log = client.images.build(
            path=str(site_dir),
            dockerfile=str(dockerfile_path),
            rm=True,
            container_limits=resource_limits,  # type: ignore[assignment]
            tag=str(site),
        )
    except docker.errors.BuildError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "user_error": True,
                "description": "Failed to build image",
                "explanation": e.msg,
                "traceback": tuple(e.build_log),
            },
        ) from e
    except docker.errors.APIError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "user_error": True,
                "description": "Failed to build image",
                "explanation": e.explanation,
            },
        ) from e

    return {"build_stdout": tuple(log)}


@router.post("/image/delete")
def delete_image(site: SiteInfo):
    client = docker.from_env()
    with contextlib.suppress(docker.errors.ImageNotFound, docker.errors.APIError):
        client.images.remove(str(site))
    return {}


@router.post("/service/update")
def update_docker_service(site_info: SiteInfo):
    """Creates, or updates the Docker service running the site.

    Note that this expects that a docker image exists with the correct tag.
    """
    params = services.create_service_params(site_info)
    client = docker.from_env()
    service = services.find_service_by_name(client, str(site_info))
    try:
        if service is None:
            client.services.create(**params)
        else:
            service.update(**params)
    except docker.errors.APIError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "description": "Failed to update service",
                "traceback": traceback.format_exc(),
            },
        ) from e
    return {}


@router.post("/service/delete")
def remove_docker_service(site: SiteInfo):
    client = docker.from_env()
    service = services.find_service_by_name(client, str(site))
    if service is not None:
        with contextlib.suppress(docker.errors.APIError):
            service.remove()
    return {}
