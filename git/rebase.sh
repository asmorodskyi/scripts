#!/bin/sh -e
current_branch=$(git branch | grep \* | cut -d ' ' -f2)
git checkout master
git pull
git checkout $current_branch
git rebase master
