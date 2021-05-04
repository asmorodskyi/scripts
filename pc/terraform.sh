#!/bin/sh -xe
CSP=${1:azure}
IMAGE=${2:-sles15-sp3-x8664-0-9-9-gce-build2-18}
TERRAFOR_FOLDER="/tmp/$CSP"
mkdir -p $TERRAFOR_FOLDER
cp /scripts/pc/terraform/$CSP.tf $TERRAFOR_FOLDER
cd $TERRAFOR_FOLDER
terraform init
if [ $CSP = "gce" ]; then
  terraform plan -var 'image_id=sles15-sp3-x8664-0-9-9-gce-build2-18' -var 'instance_count=1' -var 'type=n1-standard-2' -var 'region=europe-west1-b' -var 'name=openqa-suse-de' -var 'project=suse-sle-qa' -var 'tags={"openqa_ttl":"8640300"}' -out myplan
elif [ $CSP = "azure" ]; then
  terraform plan -var 'name=openqa-suse-de' -var 'tags={"openqa_ttl":"7500"}' -var 'offer=sles-15-sp2-byos' -var 'type=Standard_B1ms' -out myplan
fi
terraform apply "myplan"
