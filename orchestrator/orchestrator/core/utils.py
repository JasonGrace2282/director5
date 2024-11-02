from __future__ import annotations

import subprocess
from collections.abc import Iterable
from pathlib import Path
from subprocess import CompletedProcess

from fastapi import HTTPException, status


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


def run_commands(commands: Iterable[str]) -> list[CompletedProcess[str]]:
    """Run a list of shell commands and return their outputs.

    May raise subprocess.CalledProcessError if any command fails.
    """
    results = []
    for command in commands:
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            results.append(result)
        except subprocess.CalledProcessError:
            raise

    return results
