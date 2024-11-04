"""Settings for the orchestrator.

Usage:

    .. code-block:: pycon

        >>> from .core import settings
        >>> settings.DATA_STORAGE_PATH
        '/data'
"""

# firecracker socket configuration
SOCKET_BASE_PATH: str = "/tmp/firecracker-socket"
SOCKET_BASE_REQUEST_URL: str = "http+unix://%2Ftmp%2Ffirecracker-socket%2F"

# director config
DATA_STORAGE_PATH: str = "/data"

# firecracker config
FIRECRACKER_BIN_PATH: str = "/usr/bin/firecracker"

# VM configuration
VM_IMAGE_PATH: str = f"{DATA_STORAGE_PATH}/images/vmlinux"
VM_BOOT_ARGS: str = "console=ttyS0 reboot=k panic=1 pci=off"
VM_ROOTFS_PATH: str = f"{DATA_STORAGE_PATH}/images/rootfs.ext4"

# ip configuration
INTERNET_FACING_INTERFACE: str = "eth0"
