#!/bin/sh

API_SOCKET="/tmp/firecracker-socket/control.sock"

rm -rf "${API_SOCKET}"

/usr/bin/firecracker --api-sock "${API_SOCKET}" $@