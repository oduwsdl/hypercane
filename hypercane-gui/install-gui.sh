#!/bin/bash

set -e

echo "Installing GUI inside environment at $VIRTUAL_ENV"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
INSTALL_ALL=1
SKIP_WOOEY_INSTALL=1
JUST_TEMPLATES=1
OVERRIDE_VIRTUALENV_CHECK=0
WOOEY_DIR=${SCRIPT_DIR}/../hypercane_with_wooey

echo "using script directory '${SCRIPT_DIR}'"

while test $# -gt 0; do

    case "$1" in
        --wooey-dir) 
        shift
        WOOEY_DIR=$1
        echo "setting WOOEY_DIR to ${WOOEY_DIR}"
        ;;
        --install-all) echo "install-all"
        INSTALL_ALL=0
        ;;
        --skip-wooey-install) echo "skip-wooey-install"
        SKIP_WOOEY_INSTALL=0
        ;;
        --override-virtualenv-check)
        OVERRIDE_VIRTUALENV_CHECK=1
        ;;
        --just-templates) echo "just-templates"
        SKIP_WOOEY_INSTALL=0
        JUST_TEMPLATES=0
        ;;
    esac
    shift

done

PROJECT_NAME=`basename ${WOOEY_DIR}`
TEMPLATE_DIR=${WOOEY_DIR}/${PROJECT_NAME}/templates/wooey
STATIC_DIR=${WOOEY_DIR}/${PROJECT_NAME}/static
SETTINGS_DIR=${WOOEY_DIR}/${PROJECT_NAME}/settings
PARENT_DIR=`dirname ${WOOEY_DIR}`

echo PROJECT_NAME is ${PROJECT_NAME}
echo PARENT_DIR is ${PARENT_DIR}

if [ $OVERRIDE_VIRTUALENV_CHECK -eq 0 ]; then

    if [ -z $VIRTUAL_ENV ]; then
        echo "It does not appear that you are installing Hypercane's GUI inside a Python Virtualenv, quitting..."
        exit 255
    fi

fi

if [ $INSTALL_ALL -eq 0 ]; then
    echo "installing Hypercane"
    pip install -r requirements.txt
    pip install psycopg2
    python -m spacy download en_core_web_sm
    pip install . --use-feature=in-tree-build
    status=$?
    if [ $status -eq 2 ]; then
        pip install .
    fi
else
    pip freeze | grep hypercane > /dev/null
    status=$?

    if [ $status -eq 0 ]; then
        echo "Hypercane already installed, skipping install of Hypercane"
    else
        echo "installing Hypercane"
        pip install -r requirements.txt
        python -m spacy download en_core_web_sm
        pip install . --use-feature=in-tree-build
    fi
fi

if [ $INSTALL_ALL -eq 0 ]; then
    echo "installing specific Django version"
    pip install Django==3.1.8 # see https://github.com/wooey/Wooey/issues/334
else
    pip freeze | grep Django==3.1.8 > /dev/null
    status=$?

    if [ $status -eq 0 ]; then
        echo "Django already installed, skipping install of Django"
    else
        echo "installing specific Django version"
        pip install Django==3.1.8 # see https://github.com/wooey/Wooey/issues/334
    fi
fi

if [ $INSTALL_ALL -eq 0 ]; then
    echo "installing Wooey"
    pip install wooey
else
    pip freeze | grep wooey > /dev/null
    status=$?

    if [ $status -eq 0 ]; then
        echo "Wooey already installed, skipping install of Wooey"
    else
        echo "installing Wooey"
        pip install wooey
    fi
fi

if [ $SKIP_WOOEY_INSTALL -eq 1 ]; then

    echo "clearing out old Wooey project, if any"
    rm -rf ${WOOEY_DIR}

    echo "creating clean Wooey project ${PROJECT_NAME} at ${PARENT_DIR}"
    cd `dirname ${WOOEY_DIR}`
    wooify -p ${PROJECT_NAME}
fi


echo "installing templates into Django application at ${TEMPLATE_DIR}"
mkdir -p ${TEMPLATE_DIR}
cp -R ${SCRIPT_DIR}/templates/* ${TEMPLATE_DIR}

echo "installing static files (JS/CSS/images) into Django application at ${TEMPLATE_DIR}"
mkdir -p ${STATIC_DIR}/hypercane/{js,css,images}
# cp ${SCRIPT_DIR}/static/js/* ${STATIC_DIR}/js/
# cp ${SCRIPT_DIR}/static/css/* ${STATIC_DIR}/wooey/css/
cp ${SCRIPT_DIR}/static/images/* ${STATIC_DIR}/hypercane/images/

if [ $JUST_TEMPLATES -eq 1 ]; then
    echo "copying Django settings into Django application at ${WOOEY_DIR}"
    cp ${SCRIPT_DIR}/settings/*.py ${SETTINGS_DIR}

    echo "changing to ${WOOEY_DIR}"
    cd ${WOOEY_DIR}

    echo "adding scripts to Wooey"
    python ./manage.py addscript "${SCRIPT_DIR}/scripts/identify by Collection ID.py"
    python ./manage.py addscript "${SCRIPT_DIR}/scripts/sample by Collection ID.py"
    python ./manage.py addscript "${SCRIPT_DIR}/scripts/report by Collection ID.py"
    python ./manage.py addscript "${SCRIPT_DIR}/scripts/sample.py"
    python ./manage.py addscript "${SCRIPT_DIR}/scripts/report.py"
    python ./manage.py addscript "${SCRIPT_DIR}/scripts/synthesize.py"
    python ./manage.py addscript "${SCRIPT_DIR}/scripts/identify.py"
    python ./manage.py addscript "${SCRIPT_DIR}/scripts/filter include-only.py"
    python ./manage.py addscript "${SCRIPT_DIR}/scripts/filter exclude.py"
    python ./manage.py addscript "${SCRIPT_DIR}/scripts/cluster.py"
    python ./manage.py addscript "${SCRIPT_DIR}/scripts/score.py"
    python ./manage.py addscript "${SCRIPT_DIR}/scripts/order.py"

fi
