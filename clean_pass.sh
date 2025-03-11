#!/bin/sh -xe
echo 'export OBS_TOKEN=ddddddddddddddddd' > /home/asmorodskyi/source/gravity-cannon/token
rm -f /home/asmorodskyi/creds/ccoe/Azure.json
rm -f /home/asmorodskyi/creds/ccoe/EC2.json
rm -f /home/asmorodskyi/creds/ccoe/GCE.json
