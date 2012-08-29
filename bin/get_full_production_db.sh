#!/bin/bash
# Script that creates a fixture based on a full copy of the database,
# plus a python dictionary with all the users, and puts them both
# under /tmp/cronos/fixtures

if [[ -z $1 ]]; then
    echo "You need to specify the full path of cronos instance as first argument"
    exit
fi

TMP_PATH="/tmp/cronos/fixtures"

[[ -d ${TMP_PATH} ]] || mkdir -p ${TMP_PATH}
$1/manage.py dumpdata > ${TMP_PATH}/full_production_db.json
$1/manage.py get_all_real_accounts > ${TMP_PATH}/all_real_accounts.py
