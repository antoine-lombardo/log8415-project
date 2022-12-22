#!/bin/bash

cd /opt/mysqlcluster/home/mysqlc/bin
./mysql -uroot -e "CREATE USER 'myapp'@'%' IDENTIFIED BY 'testpwd';"
./mysql -uroot -e "GRANT ALL PRIVILEGES ON *.* TO 'myapp'@'%' IDENTIFIED BY 'testpwd' WITH GRANT OPTION MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;"
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