#!/bin/bash

export APP_MODE=STANDALONE

apt-get update
apt-get install mysql-server sysbench -y
mkdir /shared
curl https://downloads.mysql.com/docs/sakila-db.tar.gz --output /shared/sakila-db.tar.gz
tar -xf /shared/sakila-db.tar.gz -C /shared
rm /shared/sakila-db.tar.gz
chmod -R 777 /shared