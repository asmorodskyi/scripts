#!/bin/sh -x
# ad-hoc fix of qemu bug starts to happen on my machine
echo 2 > /proc/sys/net/ipv6/conf/all/forwarding
echo 2 > /proc/sys/net/ipv6/conf/all/accept_ra
echo 2 > /proc/sys/net/ipv6/conf/eth0/forwarding
echo 2 > /proc/sys/net/ipv6/conf/eth0/accept_ra
echo 2 > /proc/sys/net/ipv6/conf/default/forwarding
echo 2 > /proc/sys/net/ipv6/conf/default/accept_ra