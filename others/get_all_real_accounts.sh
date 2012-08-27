#!/bin/bash
# Script that creates a fixture based on a full copy of the database,
# plus a python dictionary with all the users, and puts them both
# under /tmp/cronos/fixtures

if [[ -z $1 ]]; then
    echo "You need to specify the full path of cronos instance as first argument"
    exit
fi

TMP_PATH="/tmp/cronos/fixtures"
CRONOS_PATH=$1

[[ -d ${TMP_PATH} ]] || mkdir -p ${TMP_PATH}
$1/manage.py dumpdata -e announcements.announcements > ${TMP_PATH}/full_production_db.json

python ${CRONOS_PATH}/others/get_all_real_accounts.py ${CRONOS_PATH} > ${TMP_PATH}/all_real_accounts.py
