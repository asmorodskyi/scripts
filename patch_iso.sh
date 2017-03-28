#!/bin/sh -xe
## Script should run on machine which has openqa-client package installed
#### Variables used by openqa-client
OPENQA_HOST='<your openQA instance>'
DISTRI_VAL='<distribution of target job group to trigger>'
VERSION_VAL='<OS version in target job group to trigger>'
FLAVOR_VAL='<flavor in target job group to trigger>'
ARCH_VAL='<architecture of target job group to trigger>'
## used to reach login server (user supose to have Export folder under login:/suse/$USERNAME/Export)
USERNAME='<NEED VALUE>'
PATH_TO_ISO='<NEED VALUE>'
PATH_TO_KERNEL='<NEED VALUE>'
ISO_NAME=$(echo $PATH_TO_ISO | grep -oP '[^/]+$')
KERNEL_NAME=$(echo $PATH_TO_KERNEL | grep -oP '[^/]+$')
if [ -z "$1" ]; then
  NEW_ISO_NAME='new.iso'
else
  NEW_ISO_NAME="$1"
fi
if [ ! -f $ISO_NAME ]; then
    wget $PATH_TO_ISO
fi
if [ ! -f $KERNEL_NAME ]; then
    wget $PATH_TO_KERNEL
fi
ISO_URL_VAL='https://w3.nue.suse.com/~'$USERNAME'/'$NEW_ISO_NAME
if [ ! -f $NEW_ISO_NAME ]; then
  mksusecd --create $NEW_ISO_NAME --kernel "./$KERNEL_NAME"  -- "./$ISO_NAME"
fi
sudo -u $USERNAME rsync --ignore-existing $NEW_ISO_NAME login:/suse/$USERNAME/Export
openqa-client --host $OPENQA_HOST isos post DISTRI=$DISTRI_VAL VERSION=$VERSION_VAL FLAVOR=$FLAVOR_VAL ARCH=$ARCH_VAL ISO_URL=$ISO_URL_VAL                