#!/bin/bash
for job in $(openqa-client --json --host openqa.suse.de jobs result=failed arch=ppc64le distri=sle version=12-SP3 build=0187 groupid=65 | jq '.jobs | .[] | .id'); do openqa-client --host openqa.suse.de jobs/$job/restart post ; done
