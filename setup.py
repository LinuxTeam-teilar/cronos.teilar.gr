#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='cronos',
    version='0.3-dev',
    description='Django application that collects announcements and other \
personal data for students of TEI of Larissa',
    author='cronos development team',
    author_email='cronos@teilar.gr',
    url='http://cronos.teilar.gr',
    license='AGPLv3',
    packages=find_packages(),
    include_package_data=True,
    data_files=[
        ('', ['LICENSE', 'manage.py']),
        ('bin', ['bin/update_cronos.sh']),
        ('bin', ['bin/logs_create_fix_perms.sh']),
        ('bin', ['bin/get_full_production_db.sh']),
        ('configs', ['configs/apache.conf']),
        ('configs', ['configs/cron.d_cronos']),
        ('configs', ['configs/logrotate.d_cronos']),
        ('configs', ['configs/logrotate.d_cronos-dev']),
        ('configs', ['configs/syslog-ng.conf']),
    ],
)
