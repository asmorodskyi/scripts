#!/bin/sh -e
target="${target:- asmorodskyi}"
git push $target && git show --no-patch --format=%B | hub pull-request -F -