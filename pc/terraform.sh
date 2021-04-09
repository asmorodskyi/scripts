#!/bin/sh -xe
IMAGE=${1:-sles15-sp3-x8664-0-9-9-gce-build2-18}
cd /scripts/pc/terraform/
terraform init
terraform plan -var 'image_id=sles15-sp3-x8664-0-9-9-gce-build2-18' -var 'instance_count=1' -var 'type=n1-standard-2' -var 'region=europe-west1-b' -var 'name=openqa-suse-de' -var 'project=suse-sle-qa' -var 'tags={"openqa_ttl":"8640300"}' -out myplan
terraform apply "myplan"
