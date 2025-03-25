"""A module for working with Docker services to run on nodes."""

import string
from pathlib import Path
from typing import Any

import docker
from docker.models.services import Service as DockerService
from docker.types import EndpointSpec, Mount, Resources, RestartPolicy, ServiceMode, UpdateConfig

from orchestrator import settings

from .schema import SiteInfo

TEMPLATE_DIR = Path(__file__).parent / "templates"


def find_service_by_name(client: docker.DockerClient, service_name: str) -> DockerService | None:
    """Get a docker swarm service by its name."""
    filtered: list[DockerService] = [
        service
        # this does a service.name.startswith(service_name) instead of an exact match
        for service in client.services.list(filters={"name": service_name})
        # so we filter for the exact match
        if service.name == service_name
    ]
    if not filtered:
        return None
    if len(filtered) > 1:
        raise ValueError(f"Multiple services with name {service_name!r}")
    return filtered[0]


def shared_swarm_params(site: SiteInfo) -> dict[str, Any]:
    """Creates the parameters common to all Docker Swarm services & containers."""
    env = site.container_env()
    host_site_dir = site.directory_path(on_host=True)

    # DEV ENV: We have to use our bind mount to create the dir on the
    # host machine, so we can't use host_site_dir
    # TODO: this is hacky, our dev environment should not leak into production code
    site_dir = site.directory_path()
    root = site_dir / ".home"
    root.mkdir(exist_ok=True, parents=True)

    (site_dir / "public").mkdir(exist_ok=True, parents=True)

    if site.type_ == "dynamic":
        image = str(site)
        mounts = [
            Mount(
                type="bind",
                source=str(host_site_dir),
                target="/site",
                read_only=False,
            ),
            Mount(
                type="bind",
                source=str(host_site_dir / ".home"),
                target="/root",
                read_only=False,
            ),
        ]
    else:
        image = "nginx:latest"
        mounts = [
            Mount(
                type="bind",
                source=str(host_site_dir / "public"),
                target="/usr/share/nginx/html",
                read_only=True,
            )
        ]

    return {
        "image": image,
        "mounts": [
            *mounts,
            Mount(
                type="tmpfs",
                source=None,
                target="/tmp",
                read_only=False,
                tmpfs_size=settings.TMP_TMPFS_SIZE,
                tmpfs_mode=0o1777,
            ),
            Mount(
                type="tmpfs",
                source=None,
                target="/run",
                read_only=False,
                tmpfs_size=settings.RUN_TMPFS_SIZE,
                tmpfs_mode=0o1777,
            ),
        ],
        "init": True,
        "user": "root",
        "tty": False,
        "env": [f"{name}={val}" for name, val in env.items()],
        "extra_hosts": {},
    }


def create_service_params(site_info: SiteInfo) -> dict[str, Any]:
    """Parameters for creating/updating a Docker Swarm service."""
    # default to looking through /site for a run.sh, for backwards compatibility
    if site_info.runfile is None:
        site_info.runfile = " ".join(
            ("/site/run.sh", "/site/private/run.sh", "/site/public/run.sh")
        )

    shell_cmd_template = string.Template((TEMPLATE_DIR / "run-site.sh").read_text())
    # note that the regex on the runfile should prevent injections
    shell_cmd = shell_cmd_template.safe_substitute(SEARCH_PATH=site_info.runfile)

    port = "80"
    extra_envs = {"PORT": port, "HOST": "0.0.0.0"}
    params = shared_swarm_params(site_info)
    params.setdefault("env", [])
    params["env"].extend(f"{name}={val}" for name, val in extra_envs.items())

    # match any hosts given
    hosts = " || ".join(f"Host(`{host}`)" for host in site_info.hosts)

    max_request_body_size = str(site_info.resource_limits.max_request_body_size)

    if site_info.type_ == "dynamic":
        params["command"] = ["sh", "-c", shell_cmd]

    # Docker by default runs with a small set of capacities,
    # so we don't need to modify them here.
    # TODO: we may want to "cap_drop" some capabilities we don't need
    params |= {
        "name": str(site_info),
        # nginx requires a writable file system
        # This is safe because for static sites, the user doesn't have
        # access to the nginx container
        "read_only": site_info.type_ == "dynamic",
        "workdir": "/site/public",
        # add to the docker swarm network, so traefik can find it
        "networks": ["director-sites"],
        # these labels dictate how traefik actually proxies the requests into the service
        "labels": {
            f"traefik.http.routers.{site_info}.rule": hosts,
            f"traefik.http.routers.{site_info}.service": str(site_info),
            f"traefik.http.routers.{site_info}.middlewares": f"max-request-{max_request_body_size}@swarm",
            f"traefik.http.services.{site_info}.loadbalancer.server.port": port,
            f"traefik.http.middlewares.max-request-{max_request_body_size}.buffering.maxRequestBodyBytes": max_request_body_size,
            "traefik.swarm.network": "director-sites",
        },
        "resources": Resources(
            cpu_limit=site_info.resource_limits.cpus,
            mem_limit=site_info.resource_limits.memory,
        ),
        "log_driver": "json-file",
        "log_driver_options": {
            # Keep minimal logs
            "max-size": "500k",
            "max-file": "1",
        },
        "hosts": params.pop("extra_hosts"),
        "stop_grace_period": 3,
        # vip = virtual IP, not `very important person`!
        "endpoint_spec": EndpointSpec(mode="vip", ports={}),
        # don't replicate the service if it's not supposed to be served
        "mode": ServiceMode(mode="replicated", replicas=int(site_info.is_served)),
        "restart_policy": RestartPolicy(condition="any", delay=5, max_attempts=5, window=0),
        "update_config": UpdateConfig(
            parallelism=1,
            order="stop-first",
            failure_action="rollback",
            max_failure_ratio=0,
            # delay and monitor are in nanoseconds (1e9 seconds)
            delay=int(5 * 1e9),
            monitor=int(5 * 1e9),
        ),
    }
    return params
