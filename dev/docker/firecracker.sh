#!/bin/sh

API_SOCKET="/tmp/firecracker-socket/control.sock"

rm -f "${API_SOCKET}"

/usr/bin/firecracker --api-sock "${API_SOCKET}" $@
