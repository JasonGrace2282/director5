FROM ghcr.io/astral-sh/uv:0.4-python3.12-alpine

ENV TZ America/New_York

WORKDIR /director5

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    PATH="/director5/.venv/bin:$PATH"

COPY pyproject.toml .
COPY uv.lock .

RUN apk update && \
    apk add libpq nodejs npm && \
    uv sync --frozen
