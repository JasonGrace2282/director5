class CONFIG:
    SOCKET_PATH: str = "/tmp/firecracker-socket/control.sock"
    SOCKET_REQUEST_URL: str = "http+unix://%2Ftmp%2Ffirecracker-socket%2Fcontrol.sock"
    INTERNET_FACING_INTERFACE: str = "eth0"
    DATA_STORAGE_PATH: str = "/data"
    VM_IMAGE_PATH: str = f"{DATA_STORAGE_PATH}/images/vmlinux"
    VM_BOOT_ARGS: str = "console=ttyS0 reboot=k panic=1 pci=off"
    VM_ROOTFS_PATH: str = f"{DATA_STORAGE_PATH}/images/rootfs.ext4"
