#!/usr/bin/env sh

WDIR=$(cd `dirname $0` && pwd)
ROOT=$(cd `dirname ${WDIR}` && pwd)

####################################
## This script pushes my selected ##
## files to my github repo on a   ##
## new branch called 'upload'     ##
####################################

cd /opt/docker/
git add .
git commit -m "$1"
git push origin master:upload
exit
