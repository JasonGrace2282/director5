FROM python:3.12.6-slim-bookworm

ENV TZ America/New_York

WORKDIR /director5

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12

COPY pyproject.toml .
COPY uv.lock .

RUN apt update && \
    pip3 install uv && \
    uv sync --locked --no-install-project
