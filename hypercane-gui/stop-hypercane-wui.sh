#!/bin/bash

echo "beginning the steps to shut down Hypercane GUI"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WOOEY_DIR=${SCRIPT_DIR}/../hypercane_with_wooey

django_pid=`cat "${WOOEY_DIR}/django-wooey.pid"`
echo "stopping Django at PID ${django_pid}"
kill ${django_pid}
echo "Django should be stopped"
rm "${WOOEY_DIR}/django-wooey.pid"

celery_pid=`cat "${WOOEY_DIR}/celery-wooey.pid"`
echo "stopping Celery at PID ${celery_pid}"
kill ${celery_pid}

echo "Celery should be stopped"
rm "${WOOEY_DIR}/celery-wooey.pid"

echo "Hypercane GUI processes should be shut down"
