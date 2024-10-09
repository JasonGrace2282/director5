#!/bin/sh

ARCH="$(uname -m)"
latest=$(wget "http://spec.ccfc.min.s3.amazonaws.com/?prefix=firecracker-ci/v1.10/x86_64/vmlinux-5.10&list-type=2" -O - 2>/dev/null | grep "(?<=<Key>)(firecracker-ci/v1.10/x86_64/vmlinux-5\.10\.[0-9]{3})(?=</Key>)" -o -P)

mkdir -p /vm/

set -e

# Download a linux kernel binary
wget --no-verbose "https://s3.amazonaws.com/spec.ccfc.min/${latest}" -O /vm/vmlinux

# Download a rootfs
wget --no-verbose "https://s3.amazonaws.com/spec.ccfc.min/firecracker-ci/v1.10/${ARCH}/ubuntu-22.04.ext4" -O /vm/rootfs.ext4

# Download the ssh key for the rootfs
wget --no-verbose "https://s3.amazonaws.com/spec.ccfc.min/firecracker-ci/v1.10/${ARCH}/ubuntu-22.04.id_rsa" -O /vm/ubuntu.id_rsa

# Set user read permission on the ssh key
chmod 400 /vm/ubuntu.id_rsa
