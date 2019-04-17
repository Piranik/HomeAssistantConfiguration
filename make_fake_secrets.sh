#!/usr/bin/env sh

WDIR=$(cd `dirname $0` && pwd)
SEED=$$



# Define faker callback
faker() {
  local key=$2 value=$3

  if echo ${key} | grep -q 'username$'; then
    value='superuser'
  elif echo ${key} | grep -q 'password$'; then
    value='5EcREt_pasSw0rd'
  else
    SEED=$(expr $SEED + 1)
    value=$(echo ${value} | awk 'BEGIN {srand('${SEED}'); OFS = ""} { n = split($0, a, ""); for (i = 1; i <= n; i++) { if (a[i] ~ /[[:digit:]]/) { new = new int(rand() * 10) } else if (a[i] ~ /[[:alpha:]]/) { new = new sprintf("%c", int(rand() * 26 + 97)) } else { new = new a[i] } }; $0 = new; print }')
  fi

  echo "$key: \"$value\""
}



# include parse_yaml function
. ${WDIR}/parse_yaml.sh

# read yaml file
eval $(parse_yaml secrets.yaml '' 'faker \"%2$s\" \"%3$s\" \"%4$s\";') >${WDIR}/fake_secrets.yaml
