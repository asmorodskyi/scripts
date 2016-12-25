#!/bin/bash
HOST="openqa.suse.de"
ARCH="ppc64le"
DISTRI="sle"
VERSION="12-SP3"
BUILD="0187"
GROUPID="65"
for job in $(openqa-client --json --host $HOST jobs result=failed arch=$ARCH distri=$DISTRI version=$VERSION build=$BUILD groupid=$GROUPID | jq '.jobs | .[] | .id'); do openqa-client --host $HOST jobs/$job/restart post ; done
