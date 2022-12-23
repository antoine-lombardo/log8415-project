#!/bin/bash

# Create a user to avoid accessing MySQL using the root user
cd /opt/mysqlcluster/home/mysqlc/bin
./mysql -uroot -e "CREATE USER 'myapp'@'%' IDENTIFIED BY 'testpwd';"
./mysql -uroot -e "GRANT ALL PRIVILEGES ON *.* TO 'myapp'@'%' IDENTIFIED BY 'testpwd' WITH GRANT OPTION MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;"