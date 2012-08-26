#!/bin/bash
# Cronos cronjob

# Variables
SCRIPTS=(
    teilar/websites
    teilar/departments
    teilar/teachers
    eclass/faculties
    eclass/lessons
    announcements/rss
)

help() {
    echo
    echo "Cronos update script"
    echo
    echo "You need to specify the path where the cronos source code resides"
    echo "with the -p argument"
    echo
    echo "Possible actions:"
    echo " - Update the repository (with -u)"
    echo " - Collect the static files (with -c)"
    echo " - Populate the database (with -d)"
    echo
    exit
}

if [[ $1 == "--help" ]]; then
    help
fi

CRONOS_PATH=
COLLECTSTATIC=
GITPULL=
DB=
while getopts p:cudhv arg; do
    case ${arg} in
        p) CRONOS_PATH=${OPTARG} ;;
        c) COLLECTSTATIC=1 ;;
        u) GITPULL=1 ;;
        d) DB=1 ;;
        v) VERBOSE=1 ;;
        h) help ;;
        *) help ;;
        ?) help ;;
    esac
done

if [[ -z ${CRONOS_PATH} ]]; then
    help
else
    # Check if the directory exists
    if [[ ! -d ${CRONOS_PATH} ]]; then
        echo "The specified path is not a directory or does not exist"
        help
        exit 1
    fi
    # Check if the directory contains cronos source code
    if [[ ! -f ${CRONOS_PATH}/manage.py ]]; then
        echo "The specified path does not point to a django app"
        help
        exit 1
    fi
    if ! grep -q cronos ${CRONOS_PATH}/manage.py; then
        echo "The specified path does not contain cronos"
        help
        exit 1
    fi
fi

pushd "${CRONOS_PATH}" > /dev/null

if [[ -n ${GITPULL} ]]; then
    [[ -n ${VERBOSE} ]] && echo "Updating the repository"
    git pull --force > /dev/null 2>&1
fi

if [[ -n ${COLLECTSTATIC} ]]; then
    [[ -n ${VERBOSE} ]] && echo "Collecting the static data"
    # Clean the directory to get rid of old files
    rm -rf scripts/*
    python manage.py collectstatic --noinput -l --ignore *.sh \
        --ignore *.conf --ignore logrotate.d* --ignore cron.d* > /dev/null
fi

if [[ -n ${DB} ]]; then
    [[ -n ${VERBOSE} ]] && echo "Populating the DB"
    [[ -n ${VERBOSE} ]] && echo "Generate the custom RSS files"
    python apps/announcements/rss_create.py

    [[ -n ${VERBOSE} ]] && echo "Populate the DB"
    for script in ${SCRIPTS[@]}; do
        [[ -n ${VERBOSE} ]] && echo "Run ${script}_data_get.py"
        python apps/${script}_data_get.py
    done
fi

popd > /dev/null
