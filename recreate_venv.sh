#!/bin/sh -xe
rm -rf ./.venv
python3 -m venv  ./.venv
venv
pip install --upgrade pip
pip install -r requirements.txt