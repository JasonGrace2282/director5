#!/bin/sh

set -e

uv sync

if [ "$1" = "django" ]; then
    cd manager
    python manage.py migrate --noinput
    # hand control over to django to handle SIGTERM
    exec python manage.py runserver 0.0.0.0:8080
elif [ "$1" = "tailwind" ]; then
    exec dev/tailwind/tailwindcss -i manager/director/static/tailwind/input.css -o manager/director/static/tailwind/build.css --config dev/tailwind/tailwind.config.js --watch --poll
else
    echo "Expected 'django' or 'tailwind'"
    exit 1
fi
