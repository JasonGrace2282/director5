from ipaddress import IPv4Interface

from pyroute2 import IPRoute, NetlinkError

from ...core.exceptions import NetworkingError


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
        raise NetworkingError(e, "An error occurred while trying to check for a tap device") from e
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

        return any(address.get("attrs")[0][1] == ip_interface.ip for address in addresses)

    except NetlinkError as e:
        raise NetworkingError(e, "An error occurred while trying to check for a tap device") from e
    finally:
        ip.close()


def ip_to_mac(beginning_mac: str, ip_interface: IPv4Interface) -> str:
    ip_parts = str(ip_interface.ip).split(".")

    # Convert the last three octets of the IP to hexadecimal
    mac_last_bytes = [f"{int(part):02X}" for part in ip_parts[1:]]

    return f"{beginning_mac}:{mac_last_bytes[0]}:{mac_last_bytes[1]}:{mac_last_bytes[2]}"
