import subprocess
from pathlib import Path
from time import sleep

import requests_unixsocket
from fastapi import APIRouter

from ...core import settings
from ...core.schema import APIError, APIResponse, DetailedAPIError
from ...core.utils import run_commands
from . import networking as net
from .schema import VMCreateRequest

vm_router = APIRouter()


@vm_router.post("/create")
async def create_vm(request: VMCreateRequest) -> APIResponse:
    # Create VM TAP device

    if net.tap_device_exists(request.name):
        return APIError(f"TAP device {request.name} already exists")

    if net.ip_exists(request.internal_ip):
        return APIError(f"The IP {request.internal_ip} has already been taken")

    su_ip = ["su", "-", settings.IP_CHANGEABLE_USER, "-c"]
    subprocess.run([*su_ip, f"ip link del {request.name}"], check=False)

    try:
        run_commands(
            [
                [*su_ip, f"ip tuntap add dev {request.name} mode tap"],
                [*su_ip, f"ip addr add {request.internal_ip} dev {request.name}"],
                [*su_ip, f"ip link set dev {request.name} up"],
            ]
        )
    except subprocess.CalledProcessError as e:
        return DetailedAPIError(
            "An error occurred while running a command to set up networking for a tap device on "
            "the host. See the errors field for more info",
            e,
        )

    subprocess.run(
        [
            *su_ip,
            f"iptables -D FORWARD -i {request.name} -o {settings.INTERNET_FACING_INTERFACE} -j ACCEPT",
        ],
        check=False,
    )

    log_dir = Path(f"{settings.DATA_STORAGE_PATH}/sites/{request.site_id}/debug")
    log_path = log_dir / "vm.log"

    log_dir.mkdir(exist_ok=True)
    log_path.touch()

    session = requests_unixsocket.Session()

    r = session.put(
        settings.SOCKET_REQUEST_URL + "/logger",
        {"log_path": log_path, "level": "Debug", "show_level": True, "show_log_origin": True},
    )

    if r.status_code != 200:
        return DetailedAPIError("An error occurred while trying to enable logging for the VM", r)

    r = session.put(
        settings.SOCKET_REQUEST_URL + "/boot-source",
        {"kernel_image_path": settings.VM_IMAGE_PATH, "boot_args": settings.VM_BOOT_ARGS},
    )

    if r.status_code != 200:
        return DetailedAPIError("An error occurred while trying to set a boot source for the VM", r)

    r = session.put(
        settings.SOCKET_REQUEST_URL + "/drives/rootfs",
        {
            "drive_id": "rootfs",
            "path_on_host": settings.VM_ROOTFS_PATH,
            "is_root_device": True,
            "is_read_only": False,
        },
    )

    if r.status_code != 200:
        return DetailedAPIError("An error occurred while trying to set a rootFS for the VM", r)

    r = session.put(
        settings.SOCKET_REQUEST_URL + f"/network-interfaces/{settings.INTERNET_FACING_INTERFACE}",
        {
            "iface_id": settings.INTERNET_FACING_INTERFACE,
            "guest_mac": net.ip_to_mac("06:00", request.internal_ip),
            "host_dev_name": request.name,
        },
    )

    if r.status_code != 200:
        return DetailedAPIError(
            "An error occurred while trying to set up a network error for the VM", r
        )

    # Firecracker handles requests async, so we need to ensure it has had time to update networking etc
    sleep(0.015)

    r = session.put(settings.SOCKET_REQUEST_URL + "/actions", {"action_type": "InstanceStart"})

    if r.status_code != 200:
        return DetailedAPIError(
            "An error occurred while trying to set up a network error for the VM", r
        )

    return APIResponse(message="VM Creation successful.")
