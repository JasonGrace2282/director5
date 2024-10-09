FROM ghcr.io/astral-sh/uv:0.4-python3.12-alpine

WORKDIR /director5

COPY pyproject.toml .
COPY uv.lock .
COPY /dev/docker/install-firecracker.sh .
COPY /dev/docker/install-linux.sh .

# Firecracker version is the version to install,
# Firecracker-dev is the prefix needed to install the rootfs images
# for VMs
ENV FIRECRACKER_VERSION=1.9.1 \
    FIRECRACKER_DEV_VERSION=1.10

ENV TZ=America/New_York

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    PATH="/director5/.venv/bin:$PATH"

RUN apk update && \
    apk add bash curl grep iptables libpq micro neovim openssh socat wget && \
    uv sync --frozen
RUN ./install-firecracker.sh && \
    ./install-linux.sh && \
    rm -f install-firecracker.sh install-linux.sh
