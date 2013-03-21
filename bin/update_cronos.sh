#!/bin/bash
# Cronos update script, it also can be run as cronjob

help() {
    echo
    echo "Cronos update script"
    echo
    echo "You need to specify the path where the cronos source code resides"
    echo "with the -p argument"
    echo
    echo "Options:"
    echo " -p <path> Path of the cronos instance"
    echo " -u        Update the repository"
    echo " -c        Collect the static files"
    echo " -r        Create the custom RSS feeds"
    echo " -d        Populate the database"
    echo
    exit
}

if [[ $1 == "--help" ]]; then
    help
fi

SCRIPTS=(
    websites
    departments
    teachers
    eclass_lessons
    rss_feeds
)

CRONOS_PATH=
COLLECTSTATIC=
GITPULL=
DB=
while getopts p:curdhv arg; do
    case ${arg} in
        p) CRONOS_PATH=${OPTARG} ;;
        c) COLLECTSTATIC=1 ;;
        u) GITPULL=1 ;;
        r) RSS=1 ;;
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
    # Create lock file
    LOCK="${CRONOS_PATH}/.update.lock"
    set -e
    if [ -e "${LOCK}" ]; then
        echo "Warning: \"${LOCK}\" already present, skipping update."
        exit 1
    fi
    touch "${LOCK}"
    trap "rm -f ${LOCK}" EXIT
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
    rm -rf static/*
    python manage.py collectstatic --noinput > /dev/null
fi

if [[ -n ${RSS} ]]; then
    [[ -n ${VERBOSE} ]] && echo "Generating the custom RSS files"
    python manage.py create_rss_feed
fi

if [[ -n ${DB} ]]; then
    [[ -n ${VERBOSE} ]] && echo "Populating the DB"
    for script in ${SCRIPTS[@]}; do
        [[ -n ${VERBOSE} ]] && echo "Run manage.py get_${script}"
        python manage.py get_${script}
    done
fi

popd > /dev/null
