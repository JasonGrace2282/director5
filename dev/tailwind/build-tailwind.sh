#!/bin/sh

set -e
cd ../../

./dev/tailwind/tailwindcss -i manager/director/static/tailwind/input.css -o manager/director/static/tailwind/build.css --config dev/tailwind/tailwind.config.js --build

echo Done building - build.css is now ready for production.