#!/bin/bash

function run_command() {
    text_to_print=$1
    command_to_run=$2
    error_text=$3
    newline=$4

    if [ -z $newline ]; then
        newline="yes"
    fi

    printf "${text_to_print} [    ]"

    command_output_file=`mktemp`

    set +e

    eval "$command_to_run" > $command_output_file 2>&1
    status=$?

    printf "\b\b\b\b\b\b"
    if [ $status -ne 0 ]; then
        
        printf "[FAIL]\n"
        echo
        cat "$command_output_file"
        echo
        echo "${text_to_print} FAILED"
        echo
        echo "${error_text}"
        exit 2
    fi

    if [ $newline == "nonewline" ]; then
        printf "[ OK ]"
    else
        printf "[ OK ]\n"
    fi

    set -e
}

MONGODB_URL=$1

echo "Saving caching database connection information"
echo

run_command "setting MONGODB URL to $MONGODB_URL" "echo \"HC_CACHE_STORAGE=\"$MONGODB_URL\"\" > /etc/hypercane.conf"

echo
echo "Finished saving caching database connection information"
