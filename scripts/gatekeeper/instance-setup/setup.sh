#!/bin/bash

source /scripts/common-setup-before.sh

proxy_hostname=$1
export PROXY_HOSTNAME=$slave1_hostname
export APP_MODE=GATEKEEPER

source /scripts/common-setup-after.sh