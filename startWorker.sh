#!/bin/sh -x
if [ $# -eq 0 ]; then
  systemctl stop openqa-worker@1.service
  sudo -u _openqa-worker /usr/bin/perl /usr/share/openqa/script/worker --instance 1 --no-cleanup --verbose > /openqa-worker/worker.output &
else
  kill -9 $(pgrep -U _openqa-worker)
  systemctl start openqa-worker@1.service
fi
