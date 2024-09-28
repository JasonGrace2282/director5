FROM ghcr.io/astral-sh/uv:0.4-python3.12-alpine

WORKDIR /director
ENV TZ=America/New_York \
  PYTHONUNBUFFERED=1 \
  PATH="/director/.venv/bin:$PATH"

COPY pyproject.toml .

RUN apk update && \
  apk add bash git curl && \
  ln -s /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
  uv sync --no-install-project
