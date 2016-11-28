#!/bin/bash
set -x
pushd /var/lib/openqa/tests/opensuse/
git pull origin master
pushd /var/lib/openqa/tests/opensuse/products/sle/
git pull origin master
popd
popd
