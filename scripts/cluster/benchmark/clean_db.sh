#!/bin/bash

# Cleanup the whole sakila database
cd /opt/mysqlcluster/home/mysqlc/bin
./mysql -umyapp -ptestpwd -e "drop database if exists sakila;"
./mysql -umyapp -ptestpwd -e "source /shared/sakila-db/sakila-schema.sql;"
./mysql -umyapp -ptestpwd -e "source /shared/sakila-db/sakila-data.sql;"