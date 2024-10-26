#!/bin/sh

for i in $@; do
  argv="$argv --group $i"
done

uv sync $argv
