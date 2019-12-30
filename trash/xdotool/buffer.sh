#!/bin/sh -x
WID=`xdotool search "agraul"`
xdotool windowactivate --sync $WID
xdotool type "/mnt/openqa/repo/SLE-12-SP4-Server-DVD-x86_64-Build0406-Media1/boot/x86_64/loader/linux initrd=/mnt/openqa/repo/SLE-12-SP4-Server-DVD-x86_64-Build0406-Media1/boot/x86_64/loader/initrd install=http://openqa.suse.de/assets/repo/SLE-12-SP4-Server-DVD-x86_64-Build0406-Media1?device=eth0"