#!/bin/bash
set -x
systemctl restart openqa-scheduler
systemctl restart openqa-gru
systemctl restart openqa-websockets
systemctl restart openqa-webui
systemctl restart apache2
systemctl restart openqa-worker@1
