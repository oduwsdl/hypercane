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
docker exec -it ubuntu2104test "wget -O /tmp/server-5.0.asc https://www.mongodb.org/static/pgp/server-5.0.asc"
docker exec -it ubuntu2104test "apt-key add /tmp/server-5.0.asc"
docker cp ${SCRIPT_DIR}/../ubuntu2104/mongodb-org-5.0.list ubuntu2104:/etc/apt/sources.list.d/mongodb-org-5.0.list
docker exec -it ubuntu2104 apt-get install -y mongodb-org
docker exec -it ubuntu2104 systemctl enable mongod.service
docker exec -it ubuntu2104 systemctl start mongod.service
# docker exec -it ubuntu2104test 'echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list'

echo copying $DEBFILE to container /root/ directory
docker cp $DEBFILE ubuntu2104test:/root

echo installing Hypercane
docker exec -it ubuntu2104test apt-get install -y /root/${DEBFILEBASE}

echo starting Hypercane
docker exec -it ubuntu2104test systemctl start hypercane-django.service

echo starting shell
docker exec -it ubuntu2104test /bin/bash
