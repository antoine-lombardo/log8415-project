#!/bin/bash

sysbench oltp_read_write --threads=6 --time=60 --max-requests=0 --mysql-db=sakila --mysql-user=myapp --mysql-password=testpwd run