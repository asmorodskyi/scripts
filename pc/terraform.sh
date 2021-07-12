#!/bin/sh -xe
CSP=${1:azure}
IMAGE=$2
TERRAFOR_FOLDER="/tmp/$CSP"
if [ -d $TERRAFOR_FOLDER ]; then
  rm $TERRAFOR_FOLDER/*.tf
  rm -rf $TERRAFOR_FOLDER/.terraform
fi
mkdir -p $TERRAFOR_FOLDER
cp /scripts/pc/terraform/$CSP.tf $TERRAFOR_FOLDER
cd $TERRAFOR_FOLDER
terraform init
if [ $CSP = "gce" ]; then
  terraform plan -var "image_id=$IMAGE" -var 'instance_count=1' -var 'type=n1-standard-2' -var 'region=europe-west1-b' -var 'name=openqa-suse-de' -var 'project=suse-sle-qa' -var 'tags={"openqa_ttl":"8640300"}' -out myplan
elif [ $CSP = "azure" ]; then
  terraform plan -var 'name=openqa-suse-de' -var 'tags={"openqa_ttl":"7500"}' -var 'offer=sles-15-sp2-byos' -var 'type=Standard_B1ms' -out myplan
elif [ $CSP = "ec2" ]; then
  terraform plan -no-color -var "image_id=$IMAGE" -var 'instance_count=1' -var 'type=t2.large' -var 'region=eu-west-1' -var 'name=openqa-suse-de' -var 'tags={"openqa_ttl":"8640300"}' -out myplan
fi
terraform apply "myplan"
