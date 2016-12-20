#!/bin/bash
set -x
function smart_checkout() {
  if [ "$(git symbolic-ref --short -q HEAD)" = 'master' ]; then
   git pull origin master
   elif [ -n "$(git status --porcelain)"]; then
     echo "other branch selected, but it is clean , reverting";
       git checkout master
       git pull origin master
       return $1='OK';
   else
     return $1='Fail';
   fi
}
pushd /var/lib/openqa/tests/opensuse/
smart_checkout result
if [ result = "Fail" ]; then
  echo "/var/lib/openqa/tests/opensuse/ is not a master. Exiting"
  popd
  exit 1;
fi

pushd /var/lib/openqa/tests/opensuse/products/sle/needles
smart_checkout result
if [ result = "Fail" ]; then 
   echo "/var/lib/openqa/tests/opensuse/products/sle/ is not master. Exiting"
fi

popd
popd
