#!/bin/sh -xe

username="asmorodskyi"
reponame=$(echo ${1} | grep -oP '\/[\w-]+')
reponame=${reponame:1}
servername=${1%%:*}
echo $reponame
echo $servername
git clone ${1}
cd $reponame
git remote add $username $servername:$username/$reponame.git
git fetch $username
