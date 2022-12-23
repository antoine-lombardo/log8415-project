#!/bin/bash

source /scripts/common-setup-before.sh

# Environment variables specific to the proxy instance
master_hostname=$(hostname -f)
slave1_hostname=$1
slave2_hostname=$2
slave3_hostname=$3
master_hostname=$4
public_master_hostname=$5
standalone_hostname=$6
export SLAVE1_HOSTNAME=$slave1_hostname
export SLAVE2_HOSTNAME=$slave2_hostname
export SLAVE3_HOSTNAME=$slave3_hostname
export MASTER_HOSTNAME=$master_hostname
export PUBLIC_MASTER_HOSTNAME=$public_master_hostname
export STANDALONE_HOSTNAME=$standalone_hostname
export APP_MODE=PROXY

source /scripts/common-setup-after.sh