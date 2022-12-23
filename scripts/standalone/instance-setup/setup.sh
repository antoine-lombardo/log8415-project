#!/bin/bash

source /scripts/common-setup-before.sh

# Environment variables specific to the standalone instance
export APP_MODE=STANDALONE
export DEBIAN_FRONTEND=noninteractive

# Install requirements
apt-get update
apt-get install mysql-server sysbench expect -y

# Download Sakila
mkdir /shared
curl https://downloads.mysql.com/docs/sakila-db.tar.gz --output /shared/sakila-db.tar.gz
tar -xf /shared/sakila-db.tar.gz -C /shared
rm /shared/sakila-db.tar.gz
chmod -R 777 /shared

# Secure the MySQL install
mysql -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'testpwd';"
SECURE_MYSQL=$(expect -c "
set timeout 10
spawn mysql_secure_installation
expect \"Enter password for user root:\"
send \"testpwd\r\"
expect \"Press y|Y for Yes, any other key for No:\"
send \"n\r\"
expect \"Change the password for root ?\"
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

# Create a user to avoid accessing MySQL using the root user
mysql -uroot -ptestpwd -e "DROP USER 'myapp'@'%';"
mysql -uroot -ptestpwd -e "CREATE USER 'myapp'@'%' IDENTIFIED WITH mysql_native_password BY 'testpwd';"
mysql -uroot -ptestpwd -e "GRANT ALL PRIVILEGES ON *.* TO 'myapp'@'%';"

# Clean/initialize the database
source /scripts/standalone/benchmark/clean_db.sh

source /scripts/common-setup-after.sh