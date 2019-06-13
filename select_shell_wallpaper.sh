#!/bin/sh
WALLPAPER=$(find /home/asmorodskyi/Pictures/Wallpapers/ -type f | shuf -n 1)
dconf write /com/gexperts/Tilix/background-image "'$WALLPAPER'"