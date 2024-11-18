#!/bin/sh

ARCH="$(uname -m)"
latest=$(wget "http://spec.ccfc.min.s3.amazonaws.com/?prefix=firecracker-ci/v1.10/x86_64/vmlinux-5.10&list-type=2" -O - 2>/dev/null | grep "(?<=<Key>)(firecracker-ci/v1.10/x86_64/vmlinux-5\.10\.[0-9]{3})(?=</Key>)" -o -P)

if [ -z "$latest" ]; then
  >&2 echo "Could not find the latest kernel version - try hardcoding the version?"
  exit 1
fi

mkdir -p /data/images/

set -e

# Download a linux kernel binary
wget --no-verbose "https://s3.amazonaws.com/spec.ccfc.min/${latest}" -O /data/images/vmlinux

# Download a rootfs
wget --no-verbose "https://s3.amazonaws.com/spec.ccfc.min/firecracker-ci/v1.10/${ARCH}/ubuntu-22.04.ext4" -O /data/images/rootfs.ext4

# Download the ssh key for the rootfs
wget --no-verbose "https://s3.amazonaws.com/spec.ccfc.min/firecracker-ci/v1.10/${ARCH}/ubuntu-22.04.id_rsa" -O /data/images/ubuntu.id_rsa

# Set user read permission on the ssh key
chmod 400 /data/images/ubuntu.id_rsa
