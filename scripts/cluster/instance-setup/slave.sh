#!/bin/bash

source /scripts/common-setup-before.sh
source /scripts/cluster/instance-setup/common.sh

export APP_MODE=SLAVE

mkdir -p /opt/mysqlcluster/deploy/ndb_data

source /scripts/common-setup-after.sh