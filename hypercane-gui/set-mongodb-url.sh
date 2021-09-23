#!/bin/bash

MONGODB_URL=$1

printf "setting MONGODB URL to $MONGODB_URL [    ]"
echo "HC_CACHE_STORAGE=\"$MONGODB_URL\"" > /etc/hypercane.conf
