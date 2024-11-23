import subprocess
from ipaddress import IPv4Interface
from pathlib import Path
from time import sleep

import iptc
from fastapi import APIRouter
from pyroute2 import IPRoute, NetlinkError
from requests_unixsocket import Session

from ...core import settings
from ...core.schema import APIError, APIResponse, DetailedAPIError
from ...core.utils import send_request_to_socket
from . import networking as net

vm_router = APIRouter()


@vm_router.post("/create")
async def create_vm(
    name: str,
    ip_interface: IPv4Interface,
    site_id: int,
    ram_mb: int,
    vcpu_count: int,
) -> APIResponse:
    """Create a VM.

    ## Expects
    * `site_id` must be unique
    * `name` must be the name of a tap device and socket that doesn't exist
    * `internal_ip` must not already be taken
    """
    # Create VM TAP device

    if net.tap_device_exists(name):
        return APIError(f"TAP device {name} already exists")

    if net.ip_exists(ip_interface):
        return APIError(f"The IP {ip_interface} has already been taken")

    if net.socket_exists(name):
        return APIError(f"Socket {name} already exists")

    try:
        ip = IPRoute()
        net.create_firecracker_instance(name)

        ip.link("add", ifname=name, kind="tuntap", mode="tap")
        interface_index = ip.link_lookup(ifname=name)[0]
        ip.addr(
            "add",
            index=interface_index,
            address=str(ip_interface.ip),
            prefixlen=ip_interface.network.prefixlen,
        )
        ip.link("set", ifname=name, state="up")

        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "FORWARD")
        new_rule = iptc.Rule()
        new_rule.in_interface = name
        new_rule.out_interface = settings.INTERNET_FACING_INTERFACE
        new_rule.target = iptc.Target(new_rule, "ACCEPT")

        if not any(new_rule == rule for rule in chain.rules):
            chain.insert_rule(new_rule)

    except (NetlinkError, iptc.IPTCError, subprocess.CalledProcessError) as e:
        return DetailedAPIError(
            "An error occurred while running a command to set up networking for a tap device on "
            "the host. See the errors field for more info",
            e,
        )

    log_dir = Path(f"{settings.DATA_STORAGE_PATH}/sites/{site_id}/debug")
    log_path = log_dir / "vm.log"

    log_dir.mkdir(parents=True, exist_ok=True)
    log_path.touch()

    socket_request_url = f"{settings.SOCKET_BASE_REQUEST_URL}{name}.sock"

    session = Session()

    error = send_request_to_socket(
        session,
        f"{socket_request_url}/logger",
        {
            "log_path": log_path.resolve().as_posix(),
            "level": "Debug",
            "show_level": True,
            "show_log_origin": True,
        },
    )

    if error:
        return DetailedAPIError(
            "An error occurred while trying to enable logging for the VM", error
        )

    error = send_request_to_socket(
        session,
        f"{socket_request_url}/boot-source",
        {
            "kernel_image_path": settings.VM_IMAGE_PATH,
            "boot_args": settings.VM_BOOT_ARGS,
        },
    )

    if error:
        return DetailedAPIError(
            "An error occurred while trying to set a boot source for the VM", error
        )

    error = send_request_to_socket(
        session,
        f"{socket_request_url}/drives/rootfs",
        {
            "drive_id": "rootfs",
            "path_on_host": settings.VM_ROOTFS_PATH,
            "is_root_device": True,
            "is_read_only": False,
        },
    )

    if error:
        return DetailedAPIError(
            "An error occurred while trying to set a rootFS for the VM", error
        )

    error = send_request_to_socket(
        session,
        f"{socket_request_url}/network-interfaces/{settings.INTERNET_FACING_INTERFACE}",
        {
            "iface_id": settings.INTERNET_FACING_INTERFACE,
            "guest_mac": net.ip_to_mac("06:00", ip_interface),
            "host_dev_name": name,
        },
    )

    if error:
        return DetailedAPIError(
            "An error occurred while trying to set up a network interface for the VM",
            error,
        )

    # Firecracker handles requests async, so we need to ensure it has had time to update networking etc
    sleep(0.015)

    error = send_request_to_socket(
        session,
        f"{socket_request_url}/actions",
        {"action_type": "InstanceStart"},
    )

    if error:
        return DetailedAPIError("An error occurred while trying to start the VM", error)

    return APIResponse(message="VM Creation successful.")


@vm_router.get("output/{name}")
async def get_vm_output(name: str) -> APIResponse:
    return net.get_firecracker_process_output(name)
