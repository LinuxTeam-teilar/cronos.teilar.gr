#!/bin/bash
# Cronos cronjob. It requires the application's path as argument
# TODO: Check if the path exists and it contains cronos

# Variables
CRONOS_PATH=$1
SCRIPTS=(
    teilar/websites
    teilar/departments
    teilar/teachers
    eclass/faculties
    eclass/lessons
    announcements/rss
)

pushd "${CRONOS_PATH}" > /dev/null

# Update the repository
git pull --force > /dev/null 2>&1

# Collect static data
rm -rf scripts/*
python manage.py collectstatic --noinput -l --ignore *.sh \
    --ignore *.conf --ignore logrotate > /dev/null

# Generate the custom RSS files
python apps/announcements/rss_create.py

# Update the DB
for script in ${SCRIPTS[@]}; do
    python apps/${script}_data_get.py
done
