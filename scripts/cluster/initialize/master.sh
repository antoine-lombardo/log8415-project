#!/bin/bash

# Initial setup of the database
ndb_mgm -e show
mysqld --defaults-file=/opt/mysqlcluster/deploy/conf/my.cnf --user=root &
sleep 15
SECURE_MYSQL=$(expect -c "
set timeout 10
spawn mysql_secure_installation
expect \"Enter current password for root (enter for none):\"
send \"\r\"
expect \"Change the root password?\"
send \"n\r\"
expect \"Remove anonymous users?\"
send \"y\r\"
expect \"Disallow root login remotely?\"
send \"y\r\"
expect \"Remove test database and access to it?\"
send \"y\r\"
expect \"Reload privilege tables now?\"
send \"y\r\"
expect eof
")
echo "$SECURE_MYSQL"
mysql -uroot -e "CREATE USER 'myapp'@'%' IDENTIFIED BY 'testpwd';"
mysql -uroot -e "GRANT ALL PRIVILEGES ON *.* TO 'myapp'@'%' IDENTIFIED BY 'testpwd' WITH GRANT OPTION MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;"
#mysql -umyapp -ptestpwd -e "create database clusterdb;use clusterdb;"
#mysql -umyapp -ptestpwd -e "use clusterdb;create table simples (id int not null primary key) engine=ndb;"
#mysql -umyapp -ptestpwd -e "use clusterdb;insert into simples values (1),(2),(3),(4);"
#mysql -umyapp -ptestpwd -e "use clusterdb;select * from simples;"
#+----+
#| id |
#+----+
#|  2 |
#|  3 |
#|  4 |
#|  1 |
#+----+