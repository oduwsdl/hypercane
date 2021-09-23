#!/bin/bash

set -e

function test_command(){
    command=$1

    printf "checking for command: $command [    ]"

    set +e
    which $command > /dev/null
    status=$?

    if [ $status -ne 0 ]; then
        printf "\b\b\b\b\b"
        printf "FAIL]\n"
        echo "the command '$command' is required to install Hypercane; it was not detected in your PATH"
        exit 2
    fi

    printf "\b\b\b\b\b"
    printf " OK ]\n"

    set -e
}

function test_access() {
    directory=$1
    printf "verifying that user `whoami` has write access to $directory [    ]"

    set +e
    touch ${directory}/hypercane-install-testfile.deleteme > /dev/null 2>&1
    status=$?

    printf "\b\b\b\b\b"

    if [ $status -ne 0 ]; then
        
        printf "FAIL]\n"
        echo "this installer needs to be able to write to '${directory}', which `whoami` cannot write to, please run it as a user with these permissions"
        exit 22
    fi

    rm ${directory}/hypercane-install-testfile.deleteme
    printf " OK ]\n"

    set -e
}

function run_command() {
    text_to_print=$1
    command_to_run=$2
    newline=$3

    if [ -z $newline ]; then
        newline="yes"
    fi

    printf "${text_to_print} [    ]"

    command_output_file=`mktemp`

    set +e

    # printf "running: "
    # echo "eval \"$command_to_run\" > $command_output_file"

    # echo

    eval "$command_to_run" > $command_output_file 2>&1
    status=$?

    # echo $command_output

    if [ $status -ne 0 ]; then
        printf "\b\b\b\b\b"
        printf "FAIL]\n"
        echo
        cat "$command_output_file"
        echo
        echo "${text_to_print} FAILED"
    fi

    printf "\b\b\b\b\b"

    if [ $newline == "nonewline" ]; then
        printf " OK ]"
    else
        printf " OK ]\n"
    fi

    set -e
}

function run_command() {
    text_to_print=$1
    command_to_run=$2
    newline=$3

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

function verify_absolute_path() {
    directory_to_check=$1

    printf "checking if $directory_to_check is an absolute path [    ]"
    printf "\b\b\b\b\b\b"

    if [ "${directory_to_check:0:1}" = "/" ]; then
        printf "[ OK ]\n"
        absolute_path_check=0
    else
        printf "[FAIL]\n"
        absolute_path_check=1
    fi
}

function create_hc_wrapper_script() {

    wrapper_script_path=$1

    printf "establishing wrapper script in ${wrapper_script_path}/hc for Hypercane CLI [    ]"

    set +e
    cat <<EOF > ${wrapper_script_path}/hc
#!/bin/bash
source ${INSTALL_DIRECTORY}/hypercane-virtualenv/bin/activate
${INSTALL_DIRECTORY}/hypercane-virtualenv/bin/hc \$@
EOF
    status=$?

    printf "\b\b\b\b\b\b"

    if [ $status -eq 0 ]; then
        printf "[ OK ]\n"
    else
        printf "[FAIL]\n"
        echo "FAILED: could not create Hypercane CLI wrapper script at ${wrapper_script_path}/hc"
        exit 2
    fi
    set -e
}

function check_for_systemctl() {
    printf "checking for systemctl -- does this server run systemd? [    ]"

    set +e
    which systemctl
    status=$?
    SYSTEMD_SERVER=$status

    printf "\b\b\b\b\b\b"

    if [ $status -eq 0 ]; then
        printf "[ OK ]\n"
        systemctl_check=0
    else
        printf "[ NO ]\n"
        systemctl_check=1
    fi
    set -e
}

function check_for_checkconfig() {
    printf "checking for checkconfig -- does this server use initd runlevels instead of systemd? [    ]"

    set +e
    which systemctl
    status=$?
    SYSTEMD_SERVER=$status

    printf "\b\b\b\b\b\b"

    if [ $status -eq 0 ]; then
        printf "[ OK ]\n"
        checkconfig_check=0
    else
        printf "[ NO ]\n"
        checkconfig_check=1
    fi
    set -e
}

function create_generic_startup_scripts() {

    printf "creating startup wrapper [    ]"

    set +e
    cat <<EOF > ${INSTALL_DIRECTORY}/start-hypercane-wui.sh
#!/bin/bash
source /etc/hypercane.conf
export HC_CACHE_STORAGE
${INSTALL_DIRECTORY}/hypercane-gui/start-hypercane-wui.sh --django-port ${DJANGO_PORT}
EOF
    status=$?

    printf "\b\b\b\b\b\b"

    if [ $status -eq 0 ]; then
        printf "[ OK ]\n"
    else
        printf "[FAIL]\n"
        echo "FAILED: could not create Hypercane startup wrapper"
        exit 2
    fi
    set -e

    printf "creating shutdown wrapper [    ]"

    set +e
    cat <<EOF > ${INSTALL_DIRECTORY}/stop-hypercane-wui.sh
#!/bin/bash
${INSTALL_DIRECTORY}/hypercane-gui/stop-hypercane-wui.sh
EOF
    status=$?

    printf "\b\b\b\b\b\b"

    if [ $status -eq 0 ]; then
        printf "[ OK ]\n"
    else
        printf "[FAIL]\n"
        echo "FAILED: could not create Hypercane startup wrapper"
        exit 2
    fi
    set -e

    run_command "setting permissions on startup wrapper" "chmod 0755 ${INSTALL_DIRECTORY}/start-hypercane-wui.sh"
    run_command "setting permissions on shutdown wrapper" "chmod 0755 ${INSTALL_DIRECTORY}/stop-hypercane-wui.sh"
}

function create_systemd_startup() {
    printf "creating systemd Hypercane Celery service file [    ]"

    set +e
    cat <<EOF > /etc/systemd/system/hypercane-celery.service
ExecStart=${INSTALL_DIRECTORY}/hypercane-virtualenv/bin/celery -A raintale_with_wooey worker -c 1 --beat -l info
User=${HYPERCANE_USER}
WorkingDirectory=${INSTALL_DIRECTORY}/hypercane_with_wooey
EOF

    printf "creating systemd Hypercane Django service file [    ]"

    set +e
    cat <<EOF > /etc/systemd/system/hypercane-celery.service
ExecStart=${INSTALL_DIRECTORY}/hypercane-virtualenv/bin/python manage.py runserver ${DJANGO_IP}:${DJANGO_PORT}
User=${HYPERCANE_USER}
WorkingDirectory=${INSTALL_DIRECTORY}/hypercane_with_wooey
EnvironmentFile=/etc/hypercane.conf
EOF
}

function perform_install() {

    test_command "ls"
    test_command "mkdir"
    test_command "touch"
    test_command "whoami"
    test_command "tar"
    test_command "dirname"
    test_command "python"
    test_command "virtualenv"

    test_access `dirname ${INSTALL_DIRECTORY}`
    test_access "/etc"

    run_command "setting install directory to $INSTALL_DIRECTORY" ""

    verify_absolute_path "$INSTALL_DIRECTORY"
    if [ $absolute_path_check -ne 0 ]; then
        echo "please specify an absolute path for the installation directory"    
        exit 22
    fi

    run_command "creating $INSTALL_DIRECTORY" "mkdir -p $INSTALL_DIRECTORY"
    run_command "creating ${INSTALL_DIRECTORY}/var/run" "mkdir -p $INSTALL_DIRECTORY/var/run"
    run_command "creating ${INSTALL_DIRECTORY}/var/log" "mkdir -p $INSTALL_DIRECTORY/var/log"
    run_command "removing existing virtualenv, if present" "rm -rf $INSTALL_DIRECTORY/hypercane-virtualenv"
    run_command "creating virtualenv for Hypercane" "virtualenv $INSTALL_DIRECTORY/hypercane-virtualenv"

    run_command "discovering Hypercane CLI and libraries archive" "ls hypercane*.tar.gz | grep -v 'gui'"
    CLI_TARBALL=`cat ${command_output_file}`
    run_command "discovering Hypercane GUI archive" "ls hypercane-gui-*.tar.gz"
    GUI_TARBALL=`cat ${command_output_file}`

    run_command "installing Hypercane CLI and libraries in virtualenv" "(source ${INSTALL_DIRECTORY}/hypercane-virtualenv/bin/activate && pip install ${CLI_TARBALL})"
    run_command "extracting Hypercane WUI" "tar -C ${INSTALL_DIRECTORY} -x -v -z -f ${GUI_TARBALL}"

    create_hc_wrapper_script "${WRAPPER_SCRIPT_PATH}"

    run_command "setting permissions on Hypercane CLI wrapper script" "chmod 0755 ${WRAPPER_SCRIPT_PATH}/hc"
    run_command "setting permissions on Hypercane database configuration script" "chmod 0755 ${INSTALL_DIRECTORY}/hypercane-gui/set-hypercane-database.sh"
    run_command "setting permissions on Hypercane queueing service configuration script" "chmod 0755 ${INSTALL_DIRECTORY}/hypercane-gui/set-hypercane-queueing-service.sh"
    run_command "setting permissions on Hypercane caching database configuration script" "chmod 0755 ${INSTALL_DIRECTORY}/hypercane-gui/set-caching-database.sh"
    run_command "storing MongoDB URL in /etc/hypercane.conf" "${INSTALL_DIRECTORY}/hypercane-gui/set-caching-database.sh ${HC_CACHE_STORAGE}"

    run_command "creating Hypercane WUI" "${INSTALL_DIRECTORY}/hypercane-gui/install-hypercane-wui.sh"

    check_for_systemctl
    if [ $systemctl_check -ne 0 ]; then
        check_for_checkconfig
        if [ $checkconfig_check -ne 0 ]; then
            create_generic_startup_scripts
            echo "Useful notes:"
            echo "* to start the Hypercane GUI, run ${INSTALL_DIRECTORY}/start-hypercane-wui.sh"
            echo "* to stop the Hypercane GUI, run ${INSTALL_DIRECTORY}/stop-hypercane-wui.sh"

            # TODO: check for macOS and create an icon or something in /Applications for the user to start it there
        else
            create_initd_startup
        fi
    else
        create_systemd_startup
    fi
}

# install starts here

echo
echo "Welcome to Hypercane - beginning Unix/Linux install"
echo

INSTALL_DIRECTORY="/opt/hypercane"
DJANGO_PORT=8000
DJANGO_IP="127.0.0.1"
HYPERCANE_USER="root"
WRAPPER_SCRIPT_PATH="/usr/local/bin"

while test $# -gt 0; do

    case "$1" in
        --install-directory) 
        shift
        INSTALL_DIRECTORY=$1
        ;;
        --service-port)
        shift
        DJANGO_PORT=$1
        ;;
        --mongodb-url)
        shift
        HC_CACHE_STORAGE=$1
        ;;
        --cli-wrapper-path)
        shift
        WRAPPER_SCRIPT_PATH=$1
        ;;
        --hypercane-user)
        shift
        HYPERCANE_USER=$1
        ;;
        --django_IP)
        shift
        DJANGO_IP=$1
        ;;
    esac
    shift

done

if [ -z "${HC_CACHE_STORAGE}" ]; then
    echo "ERROR: please specify the --mongodb-url option with a URL pointing to your MongoDB installation"
    exit 22
fi

perform_install $@

echo
echo "Done with Unix/Linux install. Please read the documentation for details on more setup options and how to use Hypercane."
