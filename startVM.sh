#!/bin/sh -x
virt-install --name=sle-15 --vcpus=1 --memory=1024 --cdrom=/var/lib/libvirt/images/SLE-15-Installer-DVD-x86_64-GM-DVD1.iso --disk size=36 --os-variant sle15 --graphics vnc 