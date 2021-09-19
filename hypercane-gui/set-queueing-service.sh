#!/bin/bash

set -e

echo "configuring Hypercane GUI for RabbitMQ service"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WOOEY_DIR="${SCRIPT_DIR}/../hypercane_with_wooey"

echo "WOOEY_DIR is ${WOOEY_DIR}"

POOL_LIMIT=1
CELERYD_CONCURRENCY=1

while test $# -gt 0; do

    case "$1" in
        --amqp_url)
        shift
        AMQP_URL=$1
        echo "setting AMQP URL to ${AMQP_URL}"
        ;;
        --pool_limit)
        shift
        POOL_LIMIT=$1
        echo "setting pool limit to ${POOL_LIMIT}"
        ;;
        --concurrency)
        shift
        CELERYD_CONCURRENCY=$1
        echo "setting concurrency to to ${CELERYD_CONCURRENCY}"
        ;;
    esac
    shift

done

if [[ -z ${AMQP_URL} || -z ${POOL_LIMIT} || -z ${CELERYD_CONCURRENCY}  ]]; then
    echo "An AMQP URL is required."
    echo "You are missing one of the required arguments, please rerun with the missing value supplied. This is what I have:"
    echo "--amqp_url ${AMQP_URL}"
    echo "--pool_limit ${POOL_LIMIT}"
    echo "--concurrency ${CELERYD_CONCURRENCY}"
    echo
    exit 22 #EINVAL
fi

settings_file=${WOOEY_DIR}/hypercane_with_wooey/settings/user_settings.py

cat >> ${settings_file} <<- EOF
CELERY_BROKER_URL = ${AMQP_URL}
CELERY_BROKER_POOL_LIMIT = ${POOL_LIMIT}
CELERYD_CONCURRENCY = ${CELERYD_CONCURRENCY}
CELERY_TASK_SERIALIZER = 'json'
CELERY_TASK_ACKS_LATE = True
EOF
