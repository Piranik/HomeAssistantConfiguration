#!/usr/bin/env sh

WDIR=$(cd `dirname $0` && pwd)
ROOT=$(dirname ${WDIR})

##############################################
## This script update SSL-certificates from ##
## remote host.                             ##
##############################################

# Include parse_yaml function
. ${WDIR}/_parse_yaml.sh

# Read yaml file
eval $(parse_yaml ${ROOT}/secrets.yaml)

SSH_CERT=/config/.ssh/id_rsa

CERTFILE=${secret_nas_host_ip}:/mnt/pool1/Certs/${secret_hass_domain}/fullchain.cer
KEYFILE=${secret_nas_host_ip}:/mnt/pool1/Certs/${secret_hass_domain}/${secret_hass_domain}.key

SSH_OPT="-oStrictHostKeyChecking=no"

mkdir /ssl

# Copy certs to store
scp ${SSH_OPT} -i ${SSH_CERT} ${CERTFILE} ${secret_ssl_certificate}
scp ${SSH_OPT} -i ${SSH_CERT} ${KEYFILE} ${secret_ssl_key}

exit
