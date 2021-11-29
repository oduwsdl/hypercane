#!/bin/bash

docker run --name centos8test --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro -d -p 8000:8000 local/c8-systemd
docker run --name ubuntu2104test --privileged -v /sys/fs/cgroup:/sys/fs/cgroup:ro -d -p 9000:8000 local/u2104-systemd
