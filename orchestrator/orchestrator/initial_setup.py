import subprocess

from .core.exceptions import NetworkingError
from .core.settings import CONFIG
from .core.utils import run_commands


def run_setup():
    try:
        run_commands([
            f"sudo iptables -t nat -D POSTROUTING -o {CONFIG.INTERNET_FACING_INTERFACE} -j MASQUERADE || true",
            "sudo iptables -D FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT || true",
            "sudo sh -c 'echo 1 > /proc/sys/net/ipv4/ip_forward'",
            f"sudo iptables -t nat -A POSTROUTING -o {CONFIG.INTERNET_FACING_INTERFACE} -j MASQUERADE",
            "sudo iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT",
        ])
    except subprocess.CalledProcessError as e:
        raise NetworkingError("An error occurred while running a command for initial iptables setup on "
                              "the host. See the errors field for more info", e)


if __name__ == "__main__":
    run_setup()
