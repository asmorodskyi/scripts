#!/bin/sh -xe
IMAGE=$1
ACCOUNT_KEY=$2
xz -d ./$IMAGEfixed.xz
az storage account keys list --resource-group openqa-upload --account-name openqa
az storage blob upload --max-connections 4 --account-name openqa --account-key $ACCOUNT_KEY --container-name sle-images --type page --file $IMAGEfixed --name $IMAGE
az disk create --resource-group openqa-upload --name $IMAGE --source https://openqa.blob.core.windows.net/sle-images/$IMAGE
