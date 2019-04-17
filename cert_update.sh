#!/usr/bin/env sh

WDIR=$(cd `dirname $0` && pwd)

# include parse_yaml function
. ${WDIR}/parse_yaml.sh

# read yaml file
eval $(parse_yaml secrets.yaml "secret_")

SSH_CERT=/config/.ssh/id_rsa

CERTFILE=$secret_nas_host_ip:/mnt/pool1/Certs/$secret_hass_domain/fullchain.cer
KEYFILE=$secret_nas_host_ip:/mnt/pool1/Certs/$secret_hass_domain/$secret_hass_domain.key

SSH_OPT="-oStrictHostKeyChecking=no"

mkdir /ssl

# copy certs to store
scp $SSH_OPT -i $SSH_CERT $CERTFILE '/ssl/fullchain.pem'
scp $SSH_OPT -i $SSH_CERT $KEYFILE '/ssl/privkey.pem'

exit 0
