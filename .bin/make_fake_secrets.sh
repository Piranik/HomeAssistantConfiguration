#!/usr/bin/env sh

WDIR=$(cd `dirname $0` && pwd)
ROOT=$(cd `dirname ${WDIR}` && pwd)
SEED=$$



# Define faker callback
faker() {
  local key=$2 value=$3

  if [ "$key" == "ssl_certificate" ]; then
    value='testing/example.com.fake_crt'
  elif [ "$key" == "ssl_key" ]; then
    value='testing/example.com.fake_key'
  elif [ "$key" == "home_timezone" ]; then
    value='America/Los_Angeles'
  elif echo ${key} | grep -q '\(login\|username\|password\)$'; then
    value='super_5EcREt'
  else
    SEED=$(expr ${SEED} + 1)
    value=$(echo ${value} | awk 'BEGIN {srand('${SEED}'); OFS = ""} { n = split($0, a, ""); for (i = 1; i <= n; i++) { if (a[i] ~ /[[:digit:]]/) { new = new int(rand() * 10) } else if (a[i] ~ /[[:alpha:]]/) { new = new sprintf("%c", int(rand() * 26 + 97)) } else { new = new a[i] } }; $0 = new; print }')
  fi

  echo "$key: \"$value\""
}



# Include parse_yaml function
. ${WDIR}/parse_yaml.sh

# Read real yaml file and make fake one
FPATH=${ROOT}/testing/fake_secrets.yaml
echo "# ATTENTION! This is faked file. All values filled random characters" >${FPATH}
eval $(parse_yaml ${ROOT}/secrets.yaml '' 'faker \"%2$s\" \"%3$s\" \"%4$s\";') >>${FPATH}

exit
