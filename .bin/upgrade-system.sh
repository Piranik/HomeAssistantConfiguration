#!/usr/bin/env sh

WDIR=$(cd `dirname $0` && pwd)
ROOT=$(cd `dirname ${WDIR}/..` && pwd)

###############################################
## This script upgrades the OS on my device, ##
## upgrades the docker containers, pulling   ##
## any config changes from Github if needed. ##
###############################################

cd /opt/docker
git fetch origin master
git reset --hard origin/master
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get autoremove
docker-compose pull
docker-compose down
docker-compose up -d
docker system prune -fa
docker volume prune -f
exit
