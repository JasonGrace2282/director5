from __future__ import annotations

import json
import shutil
import socket
import subprocess
from os import PathLike
from pathlib import Path
from typing import Literal


class FirecrackerError(Exception):
    type_: Literal["ip", "machine-config"]

    def __init__(self, msg: str, process: subprocess.CompletedProcess[bytes]) -> None:
        super().__init__(msg)
        self.process = process

    @property
    def stdout(self) -> str:
        return self.process.stdout.decode("utf-8")

    @property
    def stderr(self) -> str:
        return self.process.stderr.decode("utf-8")


class IpError(FirecrackerError):
    type_ = "ip"


class MachineError(FirecrackerError):
    type_ = "machine-config"


def create_vmm(api_socket: Path, tap_dev: str) -> subprocess.Popen:
    """This creates the raw VM, and sets up networking.

    It does not actually boot up the VM or anything like that.
    """
    ip = shutil.which("ip")
    assert ip is not None
    subprocess.run([ip, "link", "del", tap_dev], check=False)

    _run_cmd(
        [ip, "tuntap", "add", "dev", tap_dev, "mode", "tap"],
        "Failed creating ip link",
    )

    api_socket.unlink(missing_ok=True)

    _run_cmd(
        [ip, "link", "set", tap_dev, "master", "firecracker0"],
        "Failed adding tap devices to bridge",
    )
    _run_cmd(
        [ip, "link", "set", tap_dev, "up"],
        "Failed creating ip link",
    )
    sysctl = shutil.which("sysctl")
    assert sysctl is not None
    _run_cmd(
        [sysctl, "-w", f"net.ipv4.conf.{tap_dev}.proxy_arp=1"],
        "Failed doing first sysctl",
        MachineError,
    )
    _run_cmd(
        [sysctl, "-w", f"net.ipv6.conf.{tap_dev}.disable_ipv6=1"],
        "Failed doing first sysctl (disabling ipv6)",
        MachineError,
    )

    firecracker = shutil.which("firecracker")
    assert firecracker is not None
    return subprocess.Popen([firecracker, "--api-sock", api_socket])


def _run_cmd(
    args: list[str | PathLike],
    err_message: str,
    err: type[FirecrackerError] = IpError,
) -> subprocess.CompletedProcess[bytes]:
    """Run a command, raising an error if it fails.

    This takes care of the boilerplate of running a command.
    """
    p = subprocess.run(args, capture_output=True, check=False)
    if p.returncode != 0:
        raise err(err_message, p)
    return p


def curl_socket(
    data: dict[str, object],
    endpoint: str,
    *,
    socket_path: tuple[str, int],
    header: Literal["PUT", "GET", "POST", "DELETE", "HEAD"] = "PUT",
) -> None:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(socket_path)

        # make an HTTP request to firecracker
        body = json.dumps(data)
        request_line = f"{header} {endpoint} HTTP/1.1\r\n"
        headers = "Content-Type: application/json\r\n" f"Content-Length: {len(body)}\r\n\r\n"

        sock.sendall(request_line.encode("utf-8") + headers.encode("utf-8") + body.encode("utf-8"))
