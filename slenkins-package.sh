#!/bin/sh -e
dir="${1:-"/home/asmorodskyi/source/slenkins_hpc"}"
name="${2:-"tests-hpc"}"
destination_repository="${3:-"/home/asmorodskyi/source/Devel:SLEnkins:testsuites"}"
pushd $dir
version=$(sed -n -e 's/^Version:\s*\([0-9.]\+\)/\1/p' $name.spec)
tar --transform "s,$name,$name-${version},S" -czf $name-${version}.tgz $name/
mv $name-${version}.tgz "${destination_repository}/$name/"
cp $name.changes "${destination_repository}/$name/"
cp $name.spec "${destination_repository}/$name/"
popd