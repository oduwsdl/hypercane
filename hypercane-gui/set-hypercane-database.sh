#!/bin/bash

set -e

echo "configuring Hypercane GUI for Postgres database"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WOOEY_DIR="${SCRIPT_DIR}/../hypercane_with_wooey"

echo "WOOEY_DIR is ${WOOEY_DIR}"

if [ -z "${HC_CACHE_STORAGE}" ]; then
    echo "ERROR: Cache Storage has not been set, refusing to continue."
    exit 22
else
    echo "HC_CACHE_STORAGE is ${HC_CACHE_STORAGE}"
fi

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

# echo "got password of $DBPASSWORD"
echo "testing database connection"

echo "" | psql -h ${DBHOST} -p ${DBPORT} -U ${DBUSER} ${DBNAME}
status=$?

if [ ${status} -ne 0 ]; then
    echo "There was an issue connecting to 'postgresql://${DBUSER}:${DBHOST}:${DBPORT}/${DBNAME}', please verify the supplied database information."
fi

echo "verifying that database is empty"
export PGPASSWORD="${DBPASSWORD}"

tablecount=`echo "\dS" | psql -h ${DBHOST} -p ${DBPORT} -U ${DBUSER} ${DBNAME} | grep -P "^[ ]+public" | grep "| table" | wc -l | tr -d '[:space:]'`

echo "discovered $tablecount tables in the database"

if [ $tablecount != 0 ]; then
    echo "This script is meant to be run for a new empty database. The database at 'postgresql://${DBHOST}:${DBPORT}/${DBNAME}' contains tables from a previous install. Please drop the tables or specify a different database."
    exit
else
    echo "database is empty, continuing"
fi

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

psql -h ${DBHOST} -p ${DBPORT} -U ${DBUSER} ${DBNAME} <<EOF
ALTER TABLE wooey_scriptversion ALTER COLUMN script_path TYPE varchar(255);
CREATE TABLE IF NOT EXISTS "wooey_cache_table" (
    "cache_key" VARCHAR(255) NOT NULL PRIMARY KEY,
    "value" TEXT NOT NULL,
    "expires" TIMESTAMP NOT NULL
);
ALTER TABLE "wooey_cache_table" OWNER TO ${DBUSER}
EOF


echo "restarting Hypercane"
"${SCRIPT_DIR}/stop-hypercane-gui.sh"
"${SCRIPT_DIR}/start-hypercane-gui.sh"
echo "Hypercane should be restarted"

# add Hypercane scripts
"${SCRIPT_DIR}/add-hypercane-scripts.sh"

echo "the Postgres database and Hypercane connection settings are set up now"
