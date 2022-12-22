#!/bin/bash

mysql -umyapp -ptestpwd -e "drop database if exists sakila;"
mysql -umyapp -ptestpwd -e "source /shared/sakila-db/sakila-schema.sql;"
mysql -umyapp -ptestpwd -e "source /shared/sakila-db/sakila-data.sql;"
sysbench oltp_read_write --table-size=1000000 --mysql-host=$ip --mysql-db=sakila --mysql-user=myapp --mysql-password=testpwd prepare