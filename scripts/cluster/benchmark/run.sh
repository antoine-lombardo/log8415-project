#!/bin/bash

# Prepare and run benchmark, then cleanup entries created by sysbench
sysbench oltp_read_write --table-size=1000000 --mysql-host=127.0.0.1 --mysql-db=sakila --mysql-user=myapp --mysql-password=testpwd prepare
sysbench oltp_read_write --threads=6 --time=60 --max-requests=0 --mysql-host=127.0.0.1 --mysql-db=sakila --mysql-user=myapp --mysql-password=testpwd run
sysbench oltp_read_write --threads=6 --time=60 --max-requests=0 --mysql-host=127.0.0.1 --mysql-db=sakila --mysql-user=myapp --mysql-password=testpwd cleanup