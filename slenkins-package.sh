#!/bin/sh -e
dir="${1:-"/home/asmorodskyi/source/slenkins_source"}"
name="${2:-"tests-hpc"}"
destination_repository="${3:-"/home/asmorodskyi/source/slenkins_package"}"
current_path=$(pwd)
cd "$destination_repository/$name"
version=$(sed -n -e 's/^Version:\s*\([0-9.]\+\)/\1/p' $name.spec)
cd $dir
tar --transform "s,$name,$name-${version},S" -czf $name-${version}.tgz $name/
mv $name-${version}.tgz "${destination_repository}/$name/"
cd $current_path
