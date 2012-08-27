#!/bin/bash

[[ -d /tmp/cronos/fixtures ]] || mkdir /tmp/cronos/fixtures
$1/manage.py dumpdata -e announcements.announcements > /tmp/cronos/fixtures/full_production_db.json

python $1/others/get_all_real_accounts.py $1 > /tmp/cronos/fixtures/all_real_accounts.py
