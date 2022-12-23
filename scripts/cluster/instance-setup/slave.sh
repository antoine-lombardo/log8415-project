#!/bin/bash

source /scripts/common-setup-before.sh
source /scripts/cluster/instance-setup/common.sh

# Environment variables specific to the slave instances
export APP_MODE=SLAVE

# Create the node data work dir
mkdir -p /opt/mysqlcluster/deploy/ndb_data

source /scripts/common-setup-after.sh