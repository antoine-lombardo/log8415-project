#!/bin/bash

source /scripts/common-setup-before.sh

# Environment variables specific to the gatekeeper instance
proxy_hostname=$1
export PROXY_HOSTNAME=$proxy_hostname
export APP_MODE=GATEKEEPER

source /scripts/common-setup-after.sh