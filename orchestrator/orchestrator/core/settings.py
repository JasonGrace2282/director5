"""Settings for the orchestrator.

Usage:

    .. code-block:: pycon

        >>> from .core import settings
        >>> settings.DEBUG
        True
"""

from pathlib import Path

DEBUG = True

DOCKERFILE_IMAGES = Path("/data/images")
