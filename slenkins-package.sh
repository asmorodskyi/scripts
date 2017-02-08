#!/bin/sh -e
current_dir=$(pwd)
destination_repository='/home/asmorodskyi/source/slenkins_package'
cd "$destination_repository"
osc -A ibs build SLE_12_SP1 --no-verify --no-init; osc -A ibs build SLE_12_SP2 --no-verify --no-init
slenkins-vms.sh -i client=SLE_12_SP2_openQA-x86_64-minimal_with_sdk_installed -i server=SLE_12_SP2_openQA-x86_64-minimal_with_sdk_installed -l tests-hpc
cd $current_dir