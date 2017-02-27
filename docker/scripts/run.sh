#!/bin/bash

# Setting the working directory to the docker directory
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd $DIR/..

# Composing Application
if [[ $# > 0 ]]
then
    docker-compose $@
else
    docker-compose up
fi
