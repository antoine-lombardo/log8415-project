#!/bin/bash

# Install MySQL Cluster (needs to be done on both master and slaves)
mkdir -p /opt/mysqlcluster/home
wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz/from/http://mysql.mirrors.pair.com/ -O /opt/mysqlcluster/home/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
tar xvf /opt/mysqlcluster/home/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz -C /opt/mysqlcluster/home
ln -s /opt/mysqlcluster/home/mysql-cluster-gpl-7.2.1-linux2.6-x86_64 /opt/mysqlcluster/home/mysqlc
chmod -R 777 /opt/mysqlcluster/home/mysqlc
echo 'export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc' > /etc/profile.d/mysqlc.sh
echo 'export PATH=$MYSQLC_HOME/bin:$PATH' >> /etc/profile.d/mysqlc.sh
source /etc/profile.d/mysqlc.sh
apt -y install libncurses5