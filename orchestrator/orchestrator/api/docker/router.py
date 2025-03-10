import contextlib
import traceback
from pathlib import Path

import docker
import docker.errors
import jinja2
from fastapi import APIRouter, HTTPException

from orchestrator.core import settings

from . import services
from .parsing import parse_build_response
from .schema import ContainerCreationInfo, ContainerLimits, ExceptionInfo, SiteInfo

router = APIRouter()

TEMPLATE_DIR = Path(__file__).parent / "templates"

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    autoescape=False,
)
dockerfile_template = env.get_template("Dockerfile.j2")


def find_image_dir(site_id: int) -> Path:
    return settings.DOCKERFILE_IMAGES / f"site_{site_id}"


@router.post(
    "/create",
    responses={
        "400": {"model": ExceptionInfo},
        "500": {"model": ExceptionInfo},
    },
)
def create_container(
    site_id: int,
    base_image: str,
    maintainer: str,
    commands: list[str],
    resource_limits: ContainerLimits | None = None,
) -> ContainerCreationInfo:
    client = docker.from_env()

    dockerfile = dockerfile_template.render(
        maintainer=maintainer,
        base=base_image,
        commands=commands,
    )
    image_dir = find_image_dir(site_id)

    # In Director3, this path was the dockerfile.
    # To handle the transition, we remove it if it exists.
    if image_dir.is_file():
        image_dir.unlink()

    image_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
    dockerfile_path = image_dir / "Dockerfile"

    try:
        dockerfile_path.write_text(dockerfile)
    except OSError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "description": "Failed to create Dockerfile",
                "traceback": traceback.format_exc(),
            },
        ) from e

    # caching or storing intermediate images takes up a
    # ton of space.
    stdout_generator = client.api.build(
        str(image_dir),
        nocache=True,
        rm=True,
        forcerm=True,
        pull=False,
        decode=True,
        container_limits=resource_limits,  # type: ignore[assignment]
        tag=f"site_{site_id}",
    )
    stdout = list(stdout_generator)

    stdout, succeeded = parse_build_response(stdout)
    if not succeeded:
        # clean up the failed containers
        with contextlib.suppress(docker.errors.APIError):
            client.images.prune({"dangling": True})
        raise HTTPException(
            status_code=400,
            detail={"description": "Failed to build image", "traceback": stdout},
        )

    return {"build_stdout": stdout}


@router.post("/update-docker-service")
def update_docker_service(site_info: SiteInfo):
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
            status_code=400,
            detail={
                "description": "Failed to update service",
                "traceback": traceback.format_exc(),
            },
        ) from e
    return {}
