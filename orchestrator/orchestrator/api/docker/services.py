"""A module for working with Docker services to run on nodes."""

import shlex
from pathlib import Path
from typing import Any

import docker

from .schema import SiteInfo

TEMPLATE_DIR = Path(__file__).parent / "templates"


def create_service_params(client: docker.DockerClient, site_info: SiteInfo) -> dict[str, Any]:
    # default to looking through /site for a run.sh, for backwards compatibility
    if site_info.runfile is None:
        runfiles = ["/site/run.sh", "/site/private/run.sh", "/site/public/run.sh"]
    else:
        runfiles = [site_info.runfile]
    shell_cmd = (TEMPLATE_DIR / "run-site.sh").read_text()
    # the shlex.join function helps prevent shell injection
    shell_cmd = shell_cmd.replace("$SEARCH_PATH", shlex.join(runfiles))
    return {}
