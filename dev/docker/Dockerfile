FROM alpine:latest AS firecracker

WORKDIR /vm
COPY dev/docker/install-firecracker.sh .
RUN apk add curl tar bash && \
  ./install-firecracker.sh

FROM ghcr.io/astral-sh/uv:0.4-python3.12-alpine

COPY --from=firecracker /vm/firecracker /usr/local/bin/firecracker
COPY pyproject.toml .
COPY uv.lock .

WORKDIR /director5
ENV TZ=America/New_York
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    PATH="/director5/.venv/bin:$PATH"

RUN apk update && \
    apk add libpq bash openssh && \
    uv sync --frozen
