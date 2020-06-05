#!/bin/sh -xe
app="${1:-vault}"
filename="$app_$(date '+%j').log"
full_filename="/root/$filename"
ssh_target=root@publiccloud.qa.suse.de
ssh -t $ssh_target "cd /root/vault-docker ; docker-compose logs $app > $full_filename"
scp $ssh_target:$full_filename /tmp/$filename
