#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# we need this to be version agnostic
DEBFILE=`ls ${SCRIPT_DIR}/../../release/hypercane-*.deb`
DEBFILEBASE=`basename $DEBFILE`

echo starting container
docker run --name ubuntu2104test --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro -d -p 9000:8000 local/u2104-systemd
docker exec -it ubuntu2104test apt-get update -y

echo installing MongoDB
docker exec -it ubuntu2104test apt-get install -y wget gnupg
docker exec -it ubuntu2104test wget -O server-5.0.asc https://www.mongodb.org/static/pgp/server-5.0.asc
docker exec -it ubuntu2104test apt-key add server-5.0.asc
docker cp ${SCRIPT_DIR}/ubuntu2104/mongodb-org-5.0.list ubuntu2104test:/etc/apt/sources.list.d/mongodb-org-5.0.list
docker exec -it ubuntu2104test chown root:root /etc/apt/sources.list.d/mongodb-org-5.0.list
docker exec -it ubuntu2104test apt-get update -y
docker exec -it ubuntu2104test apt-get install -y mongodb-org
docker exec -it ubuntu2104test systemctl enable mongod.service
docker exec -it ubuntu2104test systemctl start mongod.service

echo copying $DEBFILE to container /root/ directory
docker cp $DEBFILE ubuntu2104test:/root

echo installing Hypercane
docker exec -it ubuntu2104test apt-get install -y /root/${DEBFILEBASE}

echo starting Hypercane
docker exec -it ubuntu2104test systemctl start hypercane-django.service

echo starting shell
docker exec -it ubuntu2104test /bin/bash
