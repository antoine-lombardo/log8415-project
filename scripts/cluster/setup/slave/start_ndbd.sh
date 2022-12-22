#!/bin/bash

master_hostname=$1

killall ndbd
sleep 1
cd /opt/mysqlcluster/home/mysqlc/bin
./ndbd -c $master_hostname:1186