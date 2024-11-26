#!/bin/sh

for i in $@; do
  argv="$argv --only-group $i"
done

uv sync $argv
