#!/bin/bash
set -x
pushd /var/lib/openqa/tests/opensuse/
if [ "$(git symbolic-ref --short -q HEAD)" = 'master' ]; then
 git pull origin master
 else
   echo "/var/lib/openqa/tests/opensuse/ is not a master. Exiting"
   popd
   exit 1;
 fi
pushd /var/lib/openqa/tests/opensuse/products/sle/needles
if [ "$(git symbolic-ref --short -q HEAD)" = 'master' ]; then
 git pull origin master
 else
   echo "/var/lib/openqa/tests/opensuse/products/sle/ is not master. Exiting"
fi

popd
popd
