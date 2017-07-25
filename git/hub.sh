#!/bin/sh -e
hub pull-request -m "$(git log -1 --pretty=%B)"
