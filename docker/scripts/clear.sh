#!/bin/bash

# Getting confirmation
read -p "Clear all docker containers, images, and volumes? This will erase all databases! This cannot be undone. (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Clear containers
    docker rm -f $(docker ps -a -q)
    # Clear images
    docker rmi -f $(docker images -q)
    # Clear volumes
    docker volume rm $(docker volume ls -q)
fi
