#!/usr/bin/env sh
#
# This script upgrades the OS on my device, upgrades the docker
# containers, pulling any config changes from GitHub if needed.
#
# Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
# Creative Commons BY-NC-SA 4.0 International Public License
# (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

WDIR=$(cd `dirname $0` && pwd)
ROOT=$(dirname ${WDIR})

# Include parse_yaml function
. ${WDIR}/_parse_yaml.sh

# Read yaml file
eval $(parse_yaml ${ROOT}/secrets.yaml)

cd ${ROOT}
git config user.name "${secret_git_user_name}"
git config user.email "${secret_git_user_email}"
git config core.sshCommand "ssh -i ${ROOT}/.ssh/id_rsa -oStrictHostKeyChecking=no"
git fetch origin master
git reset --hard origin/master
hassio hassos update
hassio supervisor update
hassio homeassistant update
exit
