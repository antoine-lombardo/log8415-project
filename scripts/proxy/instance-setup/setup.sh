#!/bin/bash

source /scripts/common-setup-before.sh

master_hostname=$(hostname -f)
slave1_hostname=$1
slave2_hostname=$2
slave3_hostname=$3
master_hostname=$4
export SLAVE1_HOSTNAME=$slave1_hostname
export SLAVE2_HOSTNAME=$slave2_hostname
export SLAVE3_HOSTNAME=$slave3_hostname
export MASTER_HOSTNAME=$master_hostname
export APP_MODE=PROXY

source /scripts/common-setup-after.sh