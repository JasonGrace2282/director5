from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic.networks import IPvAnyAddress
from pydantic_extra_types.mac_address import MacAddress

from .exceptions import MachineError
from .utils import _run_cmd


class CreateInstanceOut(BaseModel):
    firecracker_ip: IPvAnyAddress


class FirecrackerConfig(BaseModel):
    """A configuration object.

    Uses :meth:`.pydantic.BaseModel.dict` to convert to a dictionary that's used to configure
    firecracker. See the
    [firecracker config file](https://github.com/firecracker-microvm/firecracker/blob/a0f1c6f91cbc3a7e466492cb0d84e7f5ea659273/tests/framework/vm_config.json)
    for more details about the naming and layout.
    """

    boot_source: FirecrackerBootSource
    drives: list[FirecrackerDriveConfig]
    machine_config: FirecrackerMachineConfig = Field(serialization_alias="machine-config")
    network_interfaces: list[FirecrackerNetworkInterface] = Field(
        serialization_alias="network-interfaces"
    )

    # if needed, we can always not use the default
    cpu_config: None = None

    def create_vmm(self, api_socket: Path) -> subprocess.Popen:
        """This creates the raw VM, and sets up networking.

        It does not actually boot up the VM or anything like that.
        """
        ip = shutil.which("ip")
        assert ip is not None
        tap_dev = self.network_interfaces[0].host_dev_name
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


class FirecrackerBootSource(BaseModel):
    kernel_image_path: Path
    boot_args: str
    initrd_path: Path | None = None


class FirecrackerDriveConfig(BaseModel):
    path_on_host: Path
    socket: Path
    drive_id: str = "1"
    is_root_device: bool = True
    io_engine: str = "Sync"
    is_read_only: bool = False
    cache_type: str = "Unsafe"
    partuuid: str | None = None
    rate_limiter: None = None


class FirecrackerMachineConfig(BaseModel):
    vcpu_count: int
    mem_size_mib: int
    smt: bool
    track_dirty_pages: bool
    huge_pages: str = "None"


class FirecrackerNetworkInterface(BaseModel):
    iface_id: str
    guest_mac: MacAddress
    host_dev_name: str
