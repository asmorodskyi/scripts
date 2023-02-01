#!/bin/bash
if [ "$1" ==  'stop' ]; then
    podman stop -a
else
    CONT_TAG=$RANDOM
    podman build /home/asmorodskyi/source/pcw/ -t $CONT_TAG
    podman create --hostname pcw --name $CONT_TAG -e SECRET_KEY='$SECRET_KEY' -v /etc/pcw.ini:/etc/pcw.ini -v /home/asmorodskyi/source/pcw/db:/pcw/db -v /var/pcw:/var/pcw -p 8000:8000/tcp $CONT_TAG
	podman start $CONT_TAG
    podman logs -f $CONT_TAG
fi
