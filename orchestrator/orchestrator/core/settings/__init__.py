"""Settings for the orchestrator.

Usage:

    .. code-block:: pycon

        >>> from .core import settings
        >>> settings.DEBUG
        True
"""

import os
from pathlib import Path

DEBUG = True

DOCKERFILE_IMAGES = Path("/data/images")

TIMEZONE = "America/New_York"

SITES_DIR = Path("/data/sites")

CI = "CI" in os.environ

if DEBUG and not CI:
    compose_on_host = Path(os.environ["PWD_HOST"])
    repo_root_host = compose_on_host.parent.parent
    # note that this matches the bind mount in compose.yaml
    # we do this so that containers spawned on the host
    # still can access the site via a bind mount
    # TODO: this is hacky, our dev environment should not be
    # leaking onto production code.
    HOST_SITES_DIR = repo_root_host / "docker" / "storage" / "sites"
else:
    HOST_SITES_DIR = SITES_DIR

# Docker service configuration
TMP_TMPFS_SIZE = 10 * 1000 * 1000  # 10 MB
RUN_TMPFS_SIZE = 10 * 1000 * 100  # 10 MB
