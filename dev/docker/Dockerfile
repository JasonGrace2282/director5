FROM ghcr.io/astral-sh/uv:0.4-python3.12-bookworm

WORKDIR /director5

COPY pyproject.toml .
COPY uv.lock .

ENV TZ=America/New_York

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    PATH="/director5/.venv/bin:$PATH"

RUN apt update && \
    apt install -y curl grep iptables libpq-dev socat wget sudo \
    unzip jq iproute2 iptables iputils-ping linux-headers-generic  \
    && uv sync --frozen \
    && rm -rf /var/lib/apt/lists/*   # Reduce image size
