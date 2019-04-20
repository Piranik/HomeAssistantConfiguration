#!/usr/bin/env sh
#
# This script pulls my selected files from my GitHub repository and
# treats them as the 'master' copy
#
# Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
# Creative Commons BY-NC-SA 4.0 International Public License
# (see LICENSE.md or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#

WDIR=$(cd `dirname $0` && pwd)
ROOT=$(dirname ${WDIR})

cd ${ROOT}
git config core.sshCommand "ssh -qi ${ROOT}/.ssh/id_rsa"
git fetch origin master
git reset --hard origin/master
hassio homeassistant restart
exit
