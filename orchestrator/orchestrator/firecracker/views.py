from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from . import models

router = APIRouter(prefix="/firecracker")


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


@router.post("/create")
async def create_instance(
    site_id: int, root_image: Path, kernel_image: Path
) -> models.CreateInstanceOut:
    """Create a new Firecracker VM for the site_id provided.

    Invariant: ``site_id`` must be unique.
    """
    assert_path_exists((root_image, "root_image"), (kernel_image, "kernel_image"))

    # TODO: port https://gist.github.com/jvns/9b274f24cfa1db7abecd0d32483666a3 to python

    return models.CreateInstanceOut(ip_address="127.0.0.1")  # type: ignore[misc]
