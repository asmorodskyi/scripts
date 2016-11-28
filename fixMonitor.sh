#!/bin/bash
set -x
xrandr --output eDP-1 --auto --primary --output HDMI-1 --auto --left-of eDP-1
xrandr --output HDMI-1 --auto --primary
