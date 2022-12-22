#!/bin/bash

mysql -umyapp -ptestpwd -e "drop database if exists sakila;"
mysql -umyapp -ptestpwd -e "source /shared/sakila-db/sakila-schema.sql;"
mysql -umyapp -ptestpwd -e "source /shared/sakila-db/sakila-data.sql;"
#sysbench --test=oltp --oltp-table-size=1000000 --mysql-db=dbtest --mysql-user=myapp --mysql-password=testpwd prepare