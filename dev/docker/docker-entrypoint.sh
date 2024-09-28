#!/bin/sh

while true
do
    uv run python manager/manage.py runserver 0.0.0.0:8080
    sleep 1
done