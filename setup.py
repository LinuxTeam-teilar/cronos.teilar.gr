#!/usr/bin/env python

from setuptools import setup, find_packages
from setuptest import test
import os

'''
Rename local_settings.py in order to
be excluded from setup.py install command
'''
ORIG_NAME = 'cronos/local_settings.py'
TEMP_NAME = 'cronos/local_settings.py1'
try:
    os.rename(ORIG_NAME, TEMP_NAME)
except:
    pass

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
        ('bin', [
            'bin/update_cronos.sh',
            'bin/logs_create_fix_perms.sh',
            'bin/get_full_production_db.sh'
        ]),
        ('configs', [
            'configs/apache.conf',
            'configs/cron.d_cronos',
            'configs/logrotate.d_cronos',
            'configs/logrotate.d_cronos-dev',
            'configs/syslog-ng.conf'
        ]),
    ],
    cmdclass={'test': test},
)

'''
Restore local_settings.py
'''
try:
    os.rename(TEMP_NAME, ORIG_NAME)
except:
    pass
