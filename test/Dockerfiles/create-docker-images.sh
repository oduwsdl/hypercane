#!/bin/bash

if [ -z $VIRTUAL_ENV ]; then
    echo "It does not appear that you are building Hypercane's WUI inside a Python Virtualenv, quitting..."
    exit 255
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

if [ ! -e ${SCRIPT_DIR}/../../installer/install-hypercane.sh ]; then
    ${SCRIPT_DIR}/../../hypercane-gui/installer/linux/create-installer.sh
fi

docker build -f ${SCRIPT_DIR}/centos-dockerfile -t hypercane-wui-centos:dev .
docker build -f ${SCRIPT_DIR}/ubuntu-dockerfile -t hypercane-wui-ubuntu:dev .
