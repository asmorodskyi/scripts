#!/bin/sh -e
branch="${1:?"Branch name"}"
git fetch asmorodskyi
git checkout -b $1 asmorodskyi/$1