#!/bin/sh

set -e

uv sync
cd manager


if [ "$1" = "django" ]; then
    while true; do
      python manage.py runserver 0.0.0.0:8080
      sleep 1
    done
elif [ $1 = "tailwind" ]; then
    python manage.py tailwind install
    python manage.py tailwind start
    exec sleep infinity
else
    echo "Expected 'django' or 'tailwind'"
    exit 1
fi
