#!/bin/bash
curl 'https://openqa.suse.de/api/v1/jobs/overview?distri=sle&version=15-SP3&build=False&groupid=370' | jq -r '.[] | "openqa-client --host https://openqa.suse.de jobs/\(.id) delete # \(.name)"'
