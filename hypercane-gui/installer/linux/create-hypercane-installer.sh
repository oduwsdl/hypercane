#!/bin/sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CLI_SRC_DIR="${SCRIPT_DIR}/../../.."

function test_command(){
    command=$1

    printf "checking for $command [    ]"

    set +e
    which $command > /dev/null
    status=$?

    if [ $status -ne 0 ]; then
        printf "\b\b\b\b\b"
        printf "FAIL]\n"
        echo "$command is required to create an installer"
        exit 2
    fi

    printf "\b\b\b\b\b"
    printf " OK ]\n"

    set -e
}

function test_python_version(){
    desired_version=$1
    PYTHON_VERSION=`python --version | sed 's/Python //g' | awk -F. '{ print $1 }'`

    printf "checking for Python version ${desired_version} [    ]"

    if [ $PYTHON_VERSION -ne ${desired_version} ]; then
        printf "\b\b\b\b\b"
        printf "FAIL]\n"
        echo "Python version $PYTHON_VERSION is not supported, 3 is required."
        exit 2
    fi

    printf "\b\b\b\b\b"
    printf " OK ]\n"

}

function run_command() {
    text_to_print=$1
    command_to_run=$2
    newline=$3

    # echo "executing: ${command_to_run}"

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
        exit 2
    fi

    if [ $newline == "nonewline" ]; then
        printf "[ OK ]"
    else
        printf "[ OK ]\n"
    fi

    set -e
}

echo "STARTING: Hypercane installer build"

test_command "rm"
test_command "tar"
test_command "sed"
test_command "grep"
test_command "mktemp"
test_command "makeself"
test_command "python"
test_python_version "3"

run_command "acquiring Hypercane version" "(grep '__appversion__ = ' ${CLI_SRC_DIR}/hypercane/version.py) | sed 's/.*__appversion__ = //g'" "nonewline"
hypercane_version=`cat ${command_output_file} | sed "s/'//g"`
echo " --- Hypercane version is ${hypercane_version}"

run_command "cleaning Hypercane CLI and library build environment" "(cd ${CLI_SRC_DIR} && python ./setup.py clean 2>&1)"
run_command "cleaning Hypercane CLI and library build environment" "(cd ${CLI_SRC_DIR} && rm -rf build dist 2>&1)"
run_command "cleaning installer directory" "rm -rf ${CLI_SRC_DIR}/installer"
run_command "building Hypercane CLI and library install" "(cd ${CLI_SRC_DIR} && python ./setup.py sdist 2>&1)"

# TODO: once this has been verified to work, replace normalized_hypercane_version with just hypercane_version
normalized_hypercane_version=${hypercane_version}
# run_command "extracting normalized Hypercane version" "cat '${command_output_file}' | grep 'Normalizing .* to .*' | sed 's/.* Normalizing [^ ]* to //g'" "nonewline"

# normalized_hypercane_version=`cat ${command_output_file} | sed "s/'//g"`

# if [ -z ${normalized_hypercane_version} ]; then
#     normalized_hypercane_version=${hypercane_version}
# fi

# echo " --- Normalized Hypercane version is ${normalized_hypercane_version}"

run_command "verifying Hypercane CLI and library tarball" "ls ${CLI_SRC_DIR}/dist/hypercane-${normalized_hypercane_version}.tar.gz" "nonewline"
echo " --- ${CLI_SRC_DIR}/dist/hypercane-${normalized_hypercane_version}.tar.gz exists"

run_command "creating Hypercane GUI tarball" "tar -C ${CLI_SRC_DIR} -c -v -z -f dist/hypercane-gui-${normalized_hypercane_version}.tar.gz hypercane-gui"

run_command "verifying Hypercane GUI tarball" "ls ${CLI_SRC_DIR}/dist/hypercane-gui-${normalized_hypercane_version}.tar.gz" "nonewline"
echo " --- ${CLI_SRC_DIR}/dist/hypercane-gui-${normalized_hypercane_version}.tar.gz exists"

run_command "copying install script to archive directory" "cp ${CLI_SRC_DIR}/hypercane-gui/installer/linux/hypercane-install-script.sh ${CLI_SRC_DIR}/dist"
run_command "setting install script permissions" "chmod 0755 ${CLI_SRC_DIR}/hypercane-gui/installer/linux/hypercane-install-script.sh"
run_command "copying requirements.txt to archive directory" "cp ${CLI_SRC_DIR}/requirements.txt ${CLI_SRC_DIR}/dist"

run_command "creating directory for installer" "mkdir -p ${CLI_SRC_DIR}/installer/generic-unix"

run_command "executing makeself" "makeself ${CLI_SRC_DIR}/dist/ ${CLI_SRC_DIR}/installer/generic-unix/install-hypercane.sh 'Hypercane from the Dark and Stormy Archives Project' ./hypercane-install-script.sh"
installer_file=`cat ${command_output_file} | grep "successfully created" | sed 's/Self-extractable archive "//g' | sed 's/" successfully created.//g'`
echo "DONE: installer available at in ${installer_file}"


