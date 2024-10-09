FROM ghcr.io/astral-sh/uv:0.4-python3.12-alpine

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
    apk add bash curl libpq openssh socat && \
    uv sync --frozen
