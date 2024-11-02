"""Settings for the orchestrator.

Usage:

    .. code-block:: pycon

        >>> from .core import settings
        >>> settings.DATA_STORAGE_PATH
        '/data'
"""

# firecracker socket configuration
SOCKET_PATH: str = "/tmp/firecracker-socket/control.sock"
SOCKET_REQUEST_URL: str = "http+unix://%2Ftmp%2Ffirecracker-socket%2Fcontrol.sock"
DATA_STORAGE_PATH: str = "/data"

# VM configuration
VM_IMAGE_PATH: str = f"{DATA_STORAGE_PATH}/images/vmlinux"
VM_BOOT_ARGS: str = "console=ttyS0 reboot=k panic=1 pci=off"
VM_ROOTFS_PATH: str = f"{DATA_STORAGE_PATH}/images/rootfs.ext4"

# ip configuration
INTERNET_FACING_INTERFACE: str = "eth0"
IP_CHANGEABLE_USER = "root"
