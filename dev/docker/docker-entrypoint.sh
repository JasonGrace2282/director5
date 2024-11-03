#!/bin/sh

set -e

uv sync

if [ "$1" = "django" ]; then
    cd manager
    python manage.py migrate --noinput
    # hand control over to django to handle SIGTERM
    exec python manage.py runserver 0.0.0.0:8080
elif [ "$1" = "tailwind" ]; then
    static="manager/director/static/tailwind"
    exec dev/tailwind/tailwindcss -i $static/input.css -o $static/build.css --config dev/tailwind/tailwind.config.js --watch --poll
elif [ "$1" = "fastapi" ]; then
    cd orchestrator
    exec sudo uv run fastapi dev orchestrator/main.py --host 0.0.0.0 --port 8080
else
    echo "Unknown command command $@"
    exit 1
fi
