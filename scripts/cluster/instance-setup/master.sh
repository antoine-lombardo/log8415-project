#!/bin/bash

source /scripts/common-setup-before.sh
source /scripts/cluster/instance-setup/common.sh

master_hostname=$(hostname -f)
slave1_hostname=$0
slave2_hostname=$1
slave3_hostname=$2
export SLAVE1_HOSTNAME=$slave1_hostname
export SLAVE2_HOSTNAME=$slave2_hostname
export SLAVE3_HOSTNAME=$slave3_hostname
export APP_MODE=MASTER



# Download the Sakila DB
mkdir /shared
curl https://downloads.mysql.com/docs/sakila-db.tar.gz --output /shared/sakila-db.tar.gz
tar -xf /shared/sakila-db.tar.gz -C /shared
rm /shared/sakila-db.tar.gz
chmod -R 777 /shared

# Install requirements
apt install expect sysbench -y

# Prepare the directories structure
mkdir -p /opt/mysqlcluster/deploy
mkdir /opt/mysqlcluster/deploy/conf
mkdir /opt/mysqlcluster/deploy/mysqld_data
mkdir /opt/mysqlcluster/deploy/ndb_data

# Write the Cluster config file
cat > /opt/mysqlcluster/deploy/conf/my.cnf <<- EOF
[mysqld]
ndbcluster
datadir=/opt/mysqlcluster/deploy/mysqld_data
basedir=/opt/mysqlcluster/home/mysqlc
port=3306
EOF

# Write the Node Manager config file
cat > /opt/mysqlcluster/deploy/conf/config.ini <<- EOF
[ndb_mgmd]
hostname=$master_hostname
datadir=/opt/mysqlcluster/deploy/ndb_data
nodeid=1

[ndbd default]
noofreplicas=3
datadir=/opt/mysqlcluster/deploy/ndb_data

[ndbd]
hostname=$slave1_hostname
nodeid=3

[ndbd]
hostname=$slave2_hostname
nodeid=4

[ndbd]
hostname=$slave3_hostname
nodeid=5

[mysqld]
nodeid=50
EOF

# Initialize the database
cd /opt/mysqlcluster/home/mysqlc
scripts/mysql_install_db --no-defaults --datadir=/opt/mysqlcluster/deploy/mysqld_data

# Start the Node Manager
cd /opt/mysqlcluster/home/mysqlc/bin
ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf

source /scripts/common-setup-after.sh