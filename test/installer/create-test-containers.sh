#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

docker build --rm -t local/c8-systemd -f ${SCRIPT_DIR}/centos8/centos8-systemd-Dockerfile .
docker build --rm -t local/u2104-systemd -f ${SCRIPT_DIR}/ubuntu2104/ubuntu2104-systemd-Dockerfile .
