#!/bin/bash

# Add Environment Variables
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. "$DIR"/../.env

# Scripts
MYSQL_CREATING_TESTING_DB_SCRIPT="
CREATE DATABASE IF NOT EXISTS '$MYSQL_TEST_DB';
GRANT ALL PRIVILEGES ON '$MYSQL_TEST_DB'.* TO '$MYSQL_TEST_USER'@'%' IDENTIFIED BY '$MYSQL_TEST_PASSWORD';
GRANT ALL PRIVILEGES ON '$MYSQL_TEST_DB'.* TO '$MYSQL_TEST_USER'@localhost IDENTIFIED BY '$MYSQL_TEST_PASSWORD';
FLUSH PRIVILEGES;
"

MONGO_USER_CREATION_SCRIPT="
db.createUser({
    user: '$MONGO_USER',
    pwd: '$MONGO_PASSWORD',
    roles: [{
        role: 'root',
        db: '$MONGO_DB'
    }]
})
"

MONGO_TEST_USER_CREATION_SCRIPT="
db.createUser({
    user: '$MONGO_TEST_USER',
    pwd: '$MONGO_TEST_PASSWORD',
    roles: [{
        role: 'root',
        db: '$MONGO_TEST_DB'
    }]
})
"

# Script Execution
docker exec boilerroom_mysql_1 mysql -uroot -e "$MYSQL_CREATING_TESTING_DB_SCRIPT"
docker exec boilerroom_mongo_1 mongo admin --eval "$MONGO_USER_CREATION_SCRIPT"
docker exec boilerroom_mongo_1 mongo admin --eval "$MONGO_TEST_USER_CREATION_SCRIPT"
