#!/bin/sh -e
git branch -D $(git branch --merged master | grep -v master)