#!/bin/sh -x
xrandr --output eDP-1 --auto --primary --output DP-1-1 --auto --left-of eDP-1
xrandr --output DP-1-1 --auto --primary
