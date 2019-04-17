#!/usr/bin/env sh

WDIR=$(cd `dirname $0` && pwd)
ROOT=$(cd `dirname ${WDIR}/..` && pwd)

######################################
## This script pulls my selected    ##
## files from my Github repo, and   ##
## treats them as the 'master' copy ##
######################################

cd /opt/docker
git fetch origin master
git reset --hard origin/master
docker restart homeassistant
exit
