#!/bin/sh -xe
CSP=${1:azure}
IMAGE=$2
TERRAFOR_FOLDER="/tmp/$CSP"
TERRAFORM_VERSION=0.13.4
PODMAN_EXE="podman run -v $TERRAFOR_FOLDER:/tmp/ --env-host=true -w=/tmp  -v /home/asmorodskyi/:/home/asmorodskyi hashicorp/terraform:0.13.4"
if [ -d $TERRAFOR_FOLDER ]; then
  rm $TERRAFOR_FOLDER/*.tf
  rm -rf $TERRAFOR_FOLDER/.terraform
else
  mkdir -p $TERRAFOR_FOLDER
fi
cp /scripts/pc/terraform/$CSP.tf $TERRAFOR_FOLDER
cd $TERRAFOR_FOLDER
$PODMAN_EXE init
if [ $CSP = "gce" ]; then
  $PODMAN_EXE apply -var "image_id=$IMAGE" -var 'instance_count=1' -var 'type=n1-standard-2' -var 'region=europe-west1-b' -var 'name=openqa-suse-de' -var 'project=suse-sle-qa' -auto-approve
elif [ $CSP = "azure" ]; then
  IMAGE_VAR='offer=sles-15-sp2-byos'
  if [ -z "$IMAGE" ]; then
    IMAGE_VAR="image_id=$IMAGE"
  fi
  $PODMAN_EXE apply -var 'name=openqa-suse-de' -var $IMAGE_VAR -var 'type=Standard_B1ms' -auto-approve
elif [ $CSP = "ec2" ]; then
  $PODMAN_EXE apply -var "image_id=$IMAGE" -var 'instance_count=1' -var 'type=t2.large' -var 'region=eu-central-1' -auto-approve
fi
