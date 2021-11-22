#!/bin/bash

set -e

echo "adding Hypercane scripts to Wooey"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WOOEY_DIR="${SCRIPT_DIR}/../hypercane_with_wooey"

python ${WOOEY_DIR}/manage.py addscript --group "advanced" "${SCRIPT_DIR}/scripts/identify by Collection ID.py"
python ${WOOEY_DIR}/manage.py addscript --group "advanced" "${SCRIPT_DIR}/scripts/sample by Collection ID.py"
python ${WOOEY_DIR}/manage.py addscript --group "advanced" "${SCRIPT_DIR}/scripts/report by Collection ID.py"
python ${WOOEY_DIR}/manage.py addscript --group "advanced" "${SCRIPT_DIR}/scripts/sample.py"
python ${WOOEY_DIR}/manage.py addscript --group "advanced" "${SCRIPT_DIR}/scripts/report.py"
python ${WOOEY_DIR}/manage.py addscript --group "advanced" "${SCRIPT_DIR}/scripts/synthesize.py"
python ${WOOEY_DIR}/manage.py addscript --group "advanced" "${SCRIPT_DIR}/scripts/identify.py"
python ${WOOEY_DIR}/manage.py addscript --group "advanced" "${SCRIPT_DIR}/scripts/filter include-only.py"
python ${WOOEY_DIR}/manage.py addscript --group "advanced" "${SCRIPT_DIR}/scripts/filter exclude.py"
python ${WOOEY_DIR}/manage.py addscript --group "advanced" "${SCRIPT_DIR}/scripts/cluster.py"
python ${WOOEY_DIR}/manage.py addscript --group "advanced" "${SCRIPT_DIR}/scripts/score.py"
python ${WOOEY_DIR}/manage.py addscript --group "advanced" "${SCRIPT_DIR}/scripts/order.py"

python ${WOOEY_DIR}/manage.py addscript --group "convenience" --name "Summarize a collection and save as a Raintale story file" "${SCRIPT_DIR}/scripts/Summarize collection as Raintale story file.py"
python ${WOOEY_DIR}/manage.py addscript --group "convenience" --name "Summarize archived pages and save as a Raintale story file" "${SCRIPT_DIR}/scripts/Summarize URI-Ms as Raintale story file.py"

# python ${WOOEY_DIR}/manage.py addscript --group "convenience" --name "Create a Raintale story file from original page URLs" "${SCRIPT_DIR}/scripts/Create Raintale story file from URI-Rs.py"
python ${WOOEY_DIR}/manage.py addscript --group "convenience" --name "Create a Raintale story file from archived page URLs" "${SCRIPT_DIR}/scripts/Create Raintale story file from URI-Ms.py"

python ${WOOEY_DIR}/manage.py addscript --group "convenience" --name "Generate archived page URLs from a collection" "${SCRIPT_DIR}/scripts/Generate list of archived page URLs from Collection ID.py"
python ${WOOEY_DIR}/manage.py addscript --group "convenience" --name "Generate original page URLs from a collection" "${SCRIPT_DIR}/scripts/Generate list of original page URLs from Collection ID.py"
# python ${WOOEY_DIR}/manage.py addscript --group "convenience" --name "Generate TimeMap URLs from a collection" "${SCRIPT_DIR}/scripts/Generate list of URI-Ts from Collection ID.py"

# python ${WOOEY_DIR}/manage.py addscript --group "convenience" --name "Synthesize WARCs from archived page URLs" "${SCRIPT_DIR}/scripts/Synthesize WARCs from list of archived page URLs.py"

# python ${WOOEY_DIR}/manage.py addscript --group "convenience" --name "Synthesize WARCs from a collection" "${SCRIPT_DIR}/scripts/Synthesize WARCs from Collection ID.py"



echo "done adding Hypercane scripts to Wooey"
