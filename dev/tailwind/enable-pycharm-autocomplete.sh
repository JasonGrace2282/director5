#!/bin/sh

mkdir pyc-autocomplete
cd pyc-autocomplete || exit
cp ../tailwind.config.js tailwind.config.js
npm install -D tailwindcss
npm install @tailwindcss/forms
npm install @tailwindcss/typography
npm install @tailwindcss/aspect-ratio

# Ensure package installation

npx tailwindcss -i ../../../manager/director/static/tailwind/input.css -o ../../../manager/director/static/tailwind/build.css

echo Installed tailwind using npm
echo For next steps, see ide-guide.md