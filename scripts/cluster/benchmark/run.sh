#!/bin/bash

sysbench oltp_read_write --threads=1 --time=1 --mysql-db=sakila --mysql-user=myapp --mysql-password=testpwd run