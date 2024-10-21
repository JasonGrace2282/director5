import ipaddress
import platform
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from . import models
from .subprocesses import FirecrackerError, create_vmm
from .utils import assert_path_exists

router = APIRouter(prefix="/firecracker")


@router.post("/create")
async def create_instance(
    site_id: int, root_image: Path, kernel_image: Path
) -> models.CreateInstanceOut:
    """Create a new Firecracker VM for the site_id provided.

    Invariant: `site_id` must be unique and positive.
    """
    assert_path_exists((root_image, "root_image"), (kernel_image, "kernel_image"))

    # TODO: port https://gist.github.com/jvns/9b274f24cfa1db7abecd0d32483666a3 to python
    api_socket = Path(f"/tmp/firecracker-{site_id}.sock")
    try:
        create_vmm(api_socket, f"fc-tap-{site_id}")
    except FirecrackerError as e:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail={"type": e.type_, "stdout": e.stdout, "stderr": e.stderr},
        ) from e

    # logfile = Path(f"/tmp/firecracker-{site_id}.log")
    fc_ip = ipaddress.IPv4Address(f"172.102.0.{site_id + 1}")
    gateway_ip = ipaddress.IPv4Address("172.102.0.1")
    docker_mask_long = ipaddress.IPv4Address("255.255.255.0")
    kernel_boot_args = f"console=ttyS0 reboot=k panic=1 pci=off ip={fc_ip}::{gateway_ip}:{docker_mask_long}::eth0:off"
    uname = platform.uname()
    arch = uname.machine.lower()
    if arch == "aarch64":
        kernel_boot_args = f"keep_bootcon {kernel_boot_args}"

    return models.CreateInstanceOut(firecracker_ip=fc_ip)
