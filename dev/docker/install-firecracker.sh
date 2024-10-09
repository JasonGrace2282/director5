#!/bin/sh

set -e

ARCH="$(uname -m)"
release_url="https://github.com/firecracker-microvm/firecracker/releases"

version="v1.9.1"

curl -L "${release_url}/download/${version}/firecracker-${version}-${ARCH}.tgz" | tar -xz
mv release-${version}-${ARCH}/firecracker-${version}-${ARCH} /usr/bin/firecracker
