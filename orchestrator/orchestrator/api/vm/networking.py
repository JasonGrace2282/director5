import subprocess
from ipaddress import IPv4Interface
from pathlib import Path

from pyroute2 import IPRoute, NetlinkError

from ...core import settings
from ...core.exceptions import NetworkingError
from ...core.schema import APIError, APIResponse


def tap_device_exists(device_name: str) -> bool:
    """Check if a tap device exists.

    Args:
        device_name (str): The name of the tap device.

    Returns:
        bool: True if the tap device exists, False otherwise.
    """
    ip = IPRoute()
    try:
        links = ip.get_links()

        return any(interface.get("attrs")[0][1] == device_name for interface in links)
    except NetlinkError as e:
        raise NetworkingError(
            e, "An error occurred while trying to check for a tap device"
        ) from e
    finally:
        ip.close()


def ip_exists(ip_interface: IPv4Interface) -> bool:
    """Check if an IP address exists on any interface.

    Args:
        ip_interface (str): The IP address to check.

    Returns:
        bool: True if the IP address exists, False otherwise.
    """
    ip = IPRoute()
    try:
        addresses = ip.get_addr()

        return any(
            address.get("attrs")[0][1] == ip_interface.ip for address in addresses
        )

    except NetlinkError as e:
        raise NetworkingError(
            e, "An error occurred while trying to check for a tap device"
        ) from e
    finally:
        ip.close()


def ip_to_mac(beginning_mac: str, ip_interface: IPv4Interface) -> str:
    ip_parts = str(ip_interface.ip).split(".")

    # Convert the last three octets of the IP to hexadecimal
    mac_parts = [format(int(part), "02X") for part in ip_parts]
    mac_address = ":".join(mac_parts)

    return f"{beginning_mac}:{mac_address}"


def socket_exists(name: str) -> bool:
    path = Path(settings.SOCKET_BASE_PATH) / (name + ".sock")
    return path.exists() and path.is_socket()


def create_firecracker_instance(name: str):
    """Creates a firecracker instance with a socket at `settings.SOCKET_BASE_PATH / name`"""
    socket_path = Path(settings.SOCKET_BASE_PATH) / (name + ".sock")

    if socket_exists(name):
        socket_path.unlink()

    subprocess.Popen(
        [settings.FIRECRACKER_BIN_PATH, "--api-sock", socket_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def get_firecracker_process_output(name: str) -> APIError | APIResponse:
    raise NotImplementedError


#    if name not in processes.keys():
#        return APIError(f"Couldn't find a firecracker process with name {name}")

#    stdout, stderr = processes[name].communicate(timeout=10.0)
#    stdout = stdout.decode("utf-8")
#    stderr = stderr.decode("utf-8")

#    return APIResponse(
#        message=f"Output for firecracker process {name}",
#        data={"stdout": stdout.strip(), "stderr": stderr.strip()},
#    )
