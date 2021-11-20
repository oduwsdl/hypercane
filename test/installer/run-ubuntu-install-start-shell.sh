#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# we need this to be version agnostic
DEBFILE=`ls ${SCRIPT_DIR}/../../release/hypercane-*.deb`
DEBFILEBASE=`basename $DEBFILE`

echo starting container
docker run --name ubuntu2104test --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro -d -p 9000:8000 local/u2104-systemd

echo copying $DEBFILE to container /root/ directory
docker cp $DEBFILE ubuntu2104test:/root

echo installing Hypercane
docker exec -it ubuntu2104test apt-get update -y
docker exec -it ubuntu2104test apt-get install -y /root/${DEBFILEBASE}

echo starting Hypercane
docker exec -it ubuntu2104test systemctl start hypercane-django.service

echo starting shell
docker exec -it ubuntu2104test /bin/bash
