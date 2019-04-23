#!/usr/bin/env sh
#
# This script pushes my selected files to my GitHub repository
#
# Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
# Creative Commons BY-NC-SA 4.0 International Public License
# (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

WDIR=$(cd `dirname $0` && pwd)
ROOT=$(dirname ${WDIR})

git --version || apk -q add git

# Include parse_yaml function
. ${WDIR}/_parse_yaml.sh

# Read yaml file
eval $(parse_yaml ${ROOT}/secrets.yaml)

cd ${ROOT}
git config user.name "${secret_git_user_name}"
git config user.email "${secret_git_user_email}"
git config core.sshCommand "ssh -i ${ROOT}/.ssh/id_rsa -oStrictHostKeyChecking=no"
git add .
git commit -m "$1"
git push origin master

exit
