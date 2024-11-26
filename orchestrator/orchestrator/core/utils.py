from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, status


def assert_path_exists(
    *paths: tuple[Path, str],
    status: int = status.HTTP_400_BAD_REQUEST,
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
