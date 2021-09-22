#!/bin/bash

set -e

echo "adding Hypercane scripts to Wooey"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WOOEY_DIR="${SCRIPT_DIR}/../hypercane_with_wooey"

python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/identify by Collection ID.py"
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/sample by Collection ID.py"
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/report by Collection ID.py"
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/sample.py"
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/report.py"
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/synthesize.py"
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/identify.py"
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/filter include-only.py"
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/filter exclude.py"
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/cluster.py"
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/score.py"
python ${WOOEY_DIR}/manage.py addscript "${SCRIPT_DIR}/scripts/order.py"

echo "done adding Hypercane scripts to Wooey"
