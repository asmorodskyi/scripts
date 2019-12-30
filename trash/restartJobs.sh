#!/bin/sh
HOST="openqa.suse.de"
ARCH="ppc64le"
DISTRI="sle"
VERSION="12-SP3"
BUILD="0187"
GROUPID="65"
for job in $(openqa-client --json --host $HOST jobs result=failed arch=$ARCH distri=$DISTRI version=$VERSION build=$BUILD groupid=$GROUPID | jq '.jobs | .[] | .id'); do openqa-client --host $HOST jobs/$job/restart post ; done

##TODO ## combine this to one logic
#openqa-client --host openqa.suse.de isos post DISTRI=sle VERSION=12-SP3 FLAVOR=Server-DVD-HA ARCH=x86_64 BUILD=0045@0201 BUILD_HA=0045 BUILD_HA_GEO=0040 BUILD_SDK=0064 BUILD_SLE=0201 BUILD_WE=0039
