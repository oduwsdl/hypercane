#!/bin/bash

set -e

echo "configuring Postgres database for Hypercane GUI"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WOOEY_DIR="${SCRIPT_DIR}/../hypercane_with_wooey"

echo "WOOEY_DIR is ${WOOEY_DIR}"

while test $# -gt 0; do

    case "$1" in
        --dbuser)
        shift
        DBUSER=$1
        echo "setting database username to ${DBUSER}"
        ;;
        --dbname)
        shift
        DBNAME=$1
        echo "setting database name to ${DBNAME}"
        ;;
        --dbhost)
        shift
        DBHOST=$1
        echo "setting database hostname to ${DBHOST}"
        ;;
        --dbport)
        shift
        DBPORT=$1
        echo "setting database port to ${DBPORT}"
        ;;
    esac
    shift

done

if [[ -z ${DBUSER} || -z ${DBNAME} || -z ${DBHOST} || -z ${DBPORT} ]]; then
    echo "Username, database name, database host, and database port are required."
    echo "You are missing one of the required arguments, please rerun with the missing value supplied. This is what I have:"
    echo "--dbuser ${DBUSER}"
    echo "--dbname ${DBNAME}"
    echo "--dbhost ${DBHOST}"
    echo "--dbport ${DBPORT}"
    echo
    exit 22 #EINVAL
fi

if [ -z ${DBPASSWORD} ]; then
    echo "please type the database password:"
    read -s DBPASSWORD
fi

echo "got password of $DBPASSWORD"

settings_file=${WOOEY_DIR}/hypercane_with_wooey/settings/user_settings.py

echo "writing database information to ${settings_file}"

cat >> ${settings_file} <<- EOF
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '${DBNAME}',
        'USER': '${DBUSER}',
        'PASSWORD': '${DBPASSWORD}',
        'HOST': '${DBHOST}',
        'PORT': '${DBPORT}'
    }
}
EOF

echo "creating database schema"
startdir=`pwd`
echo "changing to ${WOOEY_DIR}"
cd ${WOOEY_DIR}
python ./manage.py migrate
cd ${startdir}

echo "updating schema at database ${DBNAME} for defects"

psql ${DBNAME} <<EOF
ALTER TABLE wooey_scriptversion ALTER COLUMN script_path TYPE varchar(255);
CREATE TABLE IF NOT EXISTS "wooey_cache_table" (
    "cache_key" VARCHAR(255) NOT NULL PRIMARY KEY,
    "value" TEXT NOT NULL,
    "expires" TIMESTAMP NOT NULL
);
ALTER TABLE "wooey_cache_table" OWNER TO ${DBUSER}
EOF


echo "restarting Hypercane"
"${SCRIPT_DIR}/stop-gui.sh"
"${SCRIPT_DIR}/start-gui.sh"
echo "Hypercane should be restarted"

echo "adding scripts to Wooey"
echo "changing to ${WOOEY_DIR}"
cd ${WOOEY_DIR}
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

echo "the Postgres connection should be set up now"
