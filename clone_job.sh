#!/bin/sh
case $# in 
0)
  echo "Need to specify at least JOB ID";;
1)
  PARAMS='--skip-chained-deps'
  FROM_HOST='http://openqa.suse.de';;
2)
 PARAMS='--skip-chained-deps'
 if [ $2 -eq 1 ] ; then 
   FROM_HOST='https://openqa.opensuse.org'
 else
   FROM_HOST=$2
 fi
;;
esac
set +x 
/usr/share/openqa/script/clone_job.pl $PARAMS --from $FROM_HOST $1
