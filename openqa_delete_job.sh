#!/bin/bash
GROUPID=${1?"openQA group id needed"}
VERSION=${2?"SLE version needed"}
BUILD=${3?"build needed"}
DRY_RUN=${4?"dry run (0 - no everything else yes)"}
IDS=$(curl "https://openqa.suse.de/api/v1/jobs/overview?distri=sle&version=$VERSION&build=$BUILD&groupid=$GROUPID" | jq '.[] | .id')
IDS_ARRAY=($IDS)
for i in "${IDS_ARRAY[@]}"
do
  if [[ $DRY_RUN -eq 0 ]] ; then
    echo "DELETING JOB: $i"
    /usr/bin/openqa-client jobs/$i delete --host https://openqa.suse.de
  else
    echo "JOB TO DELETE:"
	  /usr/bin/openqa-client --json-output jobs/$i get --host https://openqa.suse.de | jq -jr '.job |"ID: ", .id," ","JOB NAME: ", .name," ","TEST SUITE: ", .test, "\n"'
  fi
done
