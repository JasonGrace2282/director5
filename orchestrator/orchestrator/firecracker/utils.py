from __future__ import annotations

import subprocess
from os import PathLike
from pathlib import Path

from fastapi import HTTPException, status

from .exceptions import FirecrackerError, IpError

__all__ = ["assert_path_exists", "_run_cmd"]


def assert_path_exists(*paths: tuple[Path, str], status: int = status.HTTP_400_BAD_REQUEST):
    """Assert that all paths are absolute and exist.

    Each ``path`` must be a tuple of the :class:`pathlib.Path`
    and the name to be used in the error message.
    """
    errors = {}
    for path, detail_prefix in paths:
        errors.setdefault(detail_prefix, [])
        if not path.is_absolute():
            errors[detail_prefix].append("Path must be absolute")
        if not path.exists():
            errors[detail_prefix].append("Path does not exist")
    if errors:
        raise HTTPException(status_code=status, detail=errors)


def _run_cmd(
    args: list[str | PathLike],
    err_message: str,
    err: type[FirecrackerError] = IpError,
) -> subprocess.CompletedProcess[bytes]:
    """Run a command, raising an error if it fails.

    This takes care of the boilerplate of running a command.
    """
    p = subprocess.run(args, capture_output=True, check=False)
    if p.returncode != 0:
        raise err(err_message, p)
    return p
