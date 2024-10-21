import platform
from pathlib import Path

from fastapi import APIRouter
from pydantic_extra_types.mac_address import MacAddress

from . import models
from .utils import assert_path_exists

router = APIRouter(prefix="/firecracker")


@router.post("/create")
async def create_instance(
    site_id: int,
    root_image: Path,
    kernel_image: Path,
    machine_config: models.FirecrackerMachineConfig,
) -> models.CreateInstanceOut:
    """Create a new Firecracker VM for the site_id provided.

    Invariant: `site_id` must be unique and positive.
    """
    assert_path_exists((root_image, "root_image"), (kernel_image, "kernel_image"))

    # TODO: port https://gist.github.com/jvns/9b274f24cfa1db7abecd0d32483666a3 to python
    ibyte = site_id + 3
    kernel_boot_args = "console=ttyS0 reboot=k panic=1 pci=off"
    uname = platform.uname()
    arch = uname.machine.lower()
    if arch == "aarch64":
        kernel_boot_args = f"keep_bootcon {kernel_boot_args}"

    boot_source = models.FirecrackerBootSource(
        kernel_image_path=kernel_image, boot_args=kernel_boot_args
    )
    drive_config = models.FirecrackerDriveConfig(
        path_on_host=root_image, socket=Path(f"/tmp/firecracker-{ibyte}.sock")
    )
    network_interface = models.FirecrackerNetworkInterface(
        iface_id="firecracker0",
        guest_mac=MacAddress(f"02:FC:00:00:00:{ibyte:02x}"),
        host_dev_name=f"fc-tap-{ibyte}",
    )

    config = models.FirecrackerConfig(
        boot_source=boot_source,
        drives=[drive_config],
        machine_config=machine_config,
        network_interfaces=[network_interface],
    )

    assert config

    raise NotImplementedError
