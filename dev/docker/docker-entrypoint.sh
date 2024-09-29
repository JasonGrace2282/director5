#!/bin/sh

cd manager

while true
do
    if [ "$1" = "django" ]; then
        python manage.py runserver 0.0.0.0:8080
    elif [ "$1" = "tailwind" ]; then
        python manage.py tailwind start
    else
        echo "Expected 'django' or 'tailwind'"
        exit 1
    fi
    sleep 1
done
