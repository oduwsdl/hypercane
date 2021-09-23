#!/bin/bash

set -e

function test_command(){
    command=$1

    printf "checking for $command [    ]"

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

function create_startup_scripts(){

    printf "creating startup wrapper [    ]"

    set +e
    cat <<EOF > ${INSTALL_DIRECTORY}/start-hypercane
#!/bin/bash
source /etc/hypercane.conf
${INSTALL_DIRECTORY}/hypercane-gui/start-hypercane-gui.sh
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
    
#     printf "creating celery startup script [    ]"

#     set +e
#     cat <<EOF > ${INSTALL_DIRECTORY}/start-hypercane-celery
# #!/bin/bash
# source ${INSTALL_DIRECTORY}/hypercane-virtualenv/bin/activate
# ${INSTALL_DIRECTORY}/hypercane-virtualenv/bin/celery -A hypercane_with_wooey worker --beat -l info > ${INSTALL_DIRECTORY}/var/log/celery-hypercane.log 2>&1 &
# celery_pid=$!
# echo $celery_pid > ${INSTALL_DIRECTORY}/var/run/celery.pid
# EOF
#     status=$?

#     printf "\b\b\b\b\b\b"

#     if [ $status -eq 0 ]; then
#         printf "[ OK ]\n"
#     else
#         printf "[FAIL]\n"
#         echo "FAILED: could not create Hypercane Celery startup script"
#         exit 2
#     fi
#     set -e

#     printf "creating celery shutdown script [    ]"

#     set +e
#     cat <<EOF > ${INSTALL_DIRECTORY}/stop-hypercane-celery
# #!/bin/bash
# celery_pid=`cat ${INSTALL_DIRECTORY}/var/run/celery.pid`
# kill ${celery_pid}
# rm ${INSTALL_DIRECTORY}/var/run/celery.pid
# EOF
#     status=$?

#     printf "\b\b\b\b\b\b"

#     if [ $status -eq 0 ]; then
#         printf "[ OK ]\n"
#     else
#         printf "[FAIL]\n"
#         echo "FAILED: could not create Hypercane Celery shutdown script"
#         exit 2
#     fi
#     set -e

#     printf "creating Hypercane Django startup script [    ]"

#     set +e
#     cat <<EOF > ${INSTALL_DIRECTORY}/start-hypercane-django
# #!/bin/bash
# source ${INSTALL_DIRECTORY}/hypercane-virtualenv/bin/activate
# python ${INSTALL_DIRECTORY}/hypercane_with_wooey/manage.py runserver 0.0.0.0:${DJANGO_PORT} > ${INSTALL_DIRECTORY}/var/log/django-hypercane.log 2>&1 &
# django_pid=$!
# echo $django_pid > ${INSTALL_DIRECTORY}/var/run/django.pid
# EOF
#     status=$?

#     printf "\b\b\b\b\b\b"

#     if [ $status -eq 0 ]; then
#         printf "[ OK ]\n"
#     else
#         printf "[FAIL]\n"
#         echo "FAILED: could not create Hypercane GUI startup script"
#         exit 2
#     fi
#     set -e

#     printf "creating Hypercane Django shutdown script [    ]"

#     set +e
#     cat <<EOF > ${INSTALL_DIRECTORY}/stop-hypercane-django
# #!/bin/bash
# django_pid=`cat ${INSTALL_DIRECTORY}/var/run/celery.pid`
# kill ${celery_pid}
# rm ${INSTALL_DIRECTORY}/var/run/celery.pid
# EOF
#     status=$?

#     printf "\b\b\b\b\b\b"

#     if [ $status -eq 0 ]; then
#         printf "[ OK ]\n"
#     else
#         printf "[FAIL]\n"
#         echo "FAILED: could not create Hypercane Celery shutdown script"
#         exit 2
#     fi
#     set -e
}

# accept install directory as argument

function main() {}
echo
echo "Welcome to Hypercane - beginning Unix/Linux install"
echo

INSTALL_DIRECTORY="/opt/hypercane"
DJANGO_PORT=8000

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
        MONGODB_URL=$1
        ;;
    esac
    shift

done

if [ -z "${HC_CACHE_STORAGE}" ]; then
    echo "ERROR: please specify the --mongodb-url option with a URL pointing to your MongoDB installation"
    exit 22
fi

test_command "ls"
test_command "mkdir"
test_command "tar"
test_command "python"
test_command "virtualenv"

run_command "setting install directory to $INSTALL_DIRECTORY" ""

printf "checking if $INSTALL_DIRECTORY is an absolute path [    ]"
printf "\b\b\b\b\b\b"

if [ "${INSTALL_DIRECTORY:0:1}" = "/" ]; then
    printf "[ OK ]\n"
else
    printf "[FAIL]\n"
    echo "please specify an absolute path for the installation directory"
    exit 2
fi

# run_command "creating $INSTALL_DIRECTORY" "mkdir -p $INSTALL_DIRECTORY"
run_command "creating ${INSTALL_DIRECTORY}/var/run" "mkdir -p $INSTALL_DIRECTORY/var/run"
run_command "creating ${INSTALL_DIRECTORY}/var/log" "mkdir -p $INSTALL_DIRECTORY/var/log"
# run_command "removing existing virtualenv, if present" "rm -rf $INSTALL_DIRECTORY/hypercane-virtualenv"
# run_command "creating virtualenv for Hypercane" "virtualenv $INSTALL_DIRECTORY/hypercane-virtualenv"

# run_command "discovering Hypercane CLI and libraries archive" "ls hypercane*.tar.gz | grep -v 'gui'"
# CLI_TARBALL=`cat ${command_output_file}`
# run_command "discovering Hypercane GUI archive" "ls hypercane-gui-*.tar.gz"
# GUI_TARBALL=`cat ${command_output_file}`

# run_command "installing Hypercane CLI and libraries in virtualenv" "(source ${INSTALL_DIRECTORY}/hypercane-virtualenv/bin/activate && pip install ${CLI_TARBALL})"
# run_command "extracting Hypercane GUI" "tar -C ${INSTALL_DIRECTORY} -x -v -z -f ${GUI_TARBALL}"

printf "establishing wrapper script in /usr/local/bin/hc for Hypercane CLI [    ]"

set +e
cat <<EOF > /usr/local/bin/hc
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
    echo "FAILED: could not create Hypercane CLI wrapper script at /usr/local/bin/hc"
    exit 2
fi
set -e

run_command "setting permissions on Hypercane CLI wrapper script" "chmod 0755 /usr/local/bin/hc"

run_command "storing MongoDB URL in /etc/hypercane.conf" "${INSTALL_DIRECTORY}/hypercane-gui/set-mongodb-url.sh ${HC_CACHE_STORAGE}"

printf "checking for systemctl -- does this server run systemd? [    ]"

set +e
which systemctl
status=$?
SYSTEMD_SERVER=$status

printf "\b\b\b\b\b\b"

if [ $status -eq 0 ]; then
    printf "[ OK ]\n"
else
    printf "[ NO ]\n"
fi
set -e

if [ $SYSTEMD_SERVER -eq 0 ]; then
    create_systemd_startup
else

    printf "checking for checkconfig -- does this server run initd runlevels instead of systemd? [    ]"

    set +e
    which systemctl
    status=$?
    INITD_SERVER=$status

    printf "\b\b\b\b\b\b"

    if [ $status -eq 0 ]; then
        printf "[ OK ]\n"
    else
        printf "[ NO ]\n"
    fi
    set -e

    if [ $INITD_SERVER -eq 0 ]; then
        echo "initd scripts not yet supported, creating startup scripts instead"
        # create_initd_startup
    fi

    create_startup_scripts

    echo "you will need to run ${INSTALL_DIRECTORY}/start-hypercane-celery and "
fi


# TODO: install Hypercane GUI service with systemd
# TODO: install celery service with systemd


# echo "where am i?"
# pwd

# echo "where am I executed from?"
# echo $USER_PWD


echo
echo "Done with Linux install. Please read the documentation for details on more setup options and how to use Hypercane."
