#!/bin/bash

containers="ubuntu2104test centos8test"

echo stopping containers $containers
docker stop $containers

echo removing containers $containers
docker rm $containers

echo containers should be removed
