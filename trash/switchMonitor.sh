#!/bin/sh -x
if [[ $# -eq 0 ]] ; then
    xrandr --output eDP-1 --off --output HDMI-1 --auto --primary
else
    xrandr --output HDMI-1 --off --output eDP-1 --auto --primary
fi