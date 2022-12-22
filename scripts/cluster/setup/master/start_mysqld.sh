#!/bin/bash

killall mysqld
sleep 1
cd /opt/mysqlcluster/home/mysqlc/bin
./mysqld --defaults-file=/opt/mysqlcluster/deploy/conf/my.cnf --user=root > /shared/mysqld.log 2>&1 &
tail -f /shared/mysqld.log | sed '/NDB Binlog: ndb tables writable/ q'
sleep 1