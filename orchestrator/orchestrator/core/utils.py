from __future__ import annotations

import subprocess
from collections.abc import Iterable, Sequence
from pathlib import Path
from subprocess import CompletedProcess

from fastapi import HTTPException, status
from requests import HTTPError
from requests_unixsocket import Session


def assert_path_exists(
    *paths: tuple[Path, str], status: int = status.HTTP_400_BAD_REQUEST
):
    """Assert that all paths are absolute and exist.

    Each ``path`` must be a tuple of the :class:`pathlib.Path`
    and the name to be used in the error message.
    """
    errors: dict[str, list[str]] = {}
    for path, detail_prefix in paths:
        errors.setdefault(detail_prefix, [])
        if not path.is_absolute():
            errors[detail_prefix].append("Path must be absolute")
        if not path.exists():
            errors[detail_prefix].append("Path does not exist")
    if errors:
        raise HTTPException(status_code=status, detail=errors)


def run_commands(commands: Iterable[Sequence[str]]) -> list[CompletedProcess[str]]:
    """Run a list of shell commands and return their outputs.

    May raise :class:`subprocess.CalledProcessError` if any command fails.
    """
    results: list[subprocess.CompletedProcess[str]] = []
    for command in commands:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        results.append(result)

    return results


def send_request_to_socket(session: Session, url: str, json: str) -> HTTPError | None:
    try:
        r = session.put(url, json)
        r.raise_for_status()
    except HTTPError as e:
        return e

    return None
