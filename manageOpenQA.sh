#!/bin/bash
if [[ $# -eq 0 ]] ; then
    echo 'Specify start or restart'
    exit 1
fi
set -x
systemctl $1 openqa-scheduler
systemctl $1 openqa-gru
systemctl $1 openqa-websockets
systemctl $1 openqa-webui
systemctl $1 apache2
systemctl $1 openqa-worker@1
