#!/bin/sh -e
git fetch asmorodskyi
git reset --hard asmorodskyi/$(git branch | grep \* | cut -d ' ' -f2)