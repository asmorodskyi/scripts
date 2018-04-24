#!/bin/sh -x
if [ $# -eq 1 ]; then
VNC_PORT=90
else
VNC_PORT=$2
fi
/usr/bin/qemu-system-x86_64 -serial file:serial0 -vga cirrus -global isa-fdc.driveA= -m 1024 -cpu qemu64 -netdev user,id=eth0 -device virtio-net,netdev=eth0,mac=52:54:00:12:34:56 -device virtio-scsi-pci,id=scsi0 -device virtio-blk,drive=hd1,serial=1 -drive file=$1,cache=unsafe,if=none,id=hd1,format=qcow2 -boot once=d,menu=on,splash-time=5000 -device usb-ehci -device usb-tablet -smp 1 -enable-kvm -no-shutdown -vnc :$VNC_PORT,share=force-shared -device virtio-serial -chardev socket,path=virtio_console,server,nowait,id=virtio_console,logfile=virtio_console.log -device virtconsole,chardev=virtio_console,name=org.openqa.console.virtio_console -monitor telnet:127.0.0.1:20152,server,nowait
