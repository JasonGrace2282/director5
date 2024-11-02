import subprocess

from ...core.exceptions import NetworkingError
from ...core.utils import run_commands


def tap_device_exists(device_name: str) -> bool:
    """Check if a tap device exists.

    Returns:
        bool: True if tap device exists, False otherwise
    """
    try:
        run_commands(["ip", "link", "show", device_name])

    except subprocess.CalledProcessError as e:
        if "does not exist" in e.stderr or "can't find" in e.stderr:
            return False
        raise NetworkingError("An error occurred while trying to check for a tap device", e) from e

    return True


def ip_exists(internal_ip: str) -> bool:
    try:
        output = run_commands(["ip", "addr", "show"])
    except subprocess.CalledProcessError as e:
        raise NetworkingError("An error occurred while trying to check for a IP address", e) from e

    return internal_ip in output


def ip_to_mac(beginning_mac: str, ip_address: str) -> str:
    ip_parts = ip_address.split(".")

    # Convert the last three octets of the IP to hexadecimal
    mac_last_bytes = [f"{int(part):02X}" for part in ip_parts[1:]]

    return f"{beginning_mac}:{mac_last_bytes[0]}:{mac_last_bytes[1]}:{mac_last_bytes[2]}"
