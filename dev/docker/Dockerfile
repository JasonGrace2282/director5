FROM ghcr.io/astral-sh/uv:0.6-python3.13-bookworm-slim

WORKDIR /director5

COPY pyproject.toml .
COPY uv.lock .

ENV TZ=America/New_York

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    UV_PROJECT_ENVIRONMENT="/venv"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev \
    && uv sync --frozen \
    && rm -rf /var/lib/apt/lists/*   # Reduce image size
