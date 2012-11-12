from setuptools import setup, find_packages
from setuptest import test
import os, sys
import cronos

try:
    if sys.argv[1] == 'install':
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
except IndexError:
    pass

setup(
    name=NAME,
    version=cronos.__version__,
    license='AGPLv3',
    author='Cronos Development Team',
    author_email='cronos@teilar.gr',
    url='http://cronos.teilar.gr',
    description='Django application that collects announcements and personal data for students of TEI of Larissa',
    keywords='rss, announcements, university, django, teilar',
    packages=find_packages(),
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
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Students',
        'License :: OSI Approved :: GNU Affero General Public License v3 (AGPLv3)',
        'Natural Language :: Greek',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
    ],
    install_requires=[
        'beautifulsoup>=3.2.1',
        'Django>=1.4.1',
        'django-setuptest>=0.1.2',
        'django-endless-pagination>=1.1',
        'django-tastypie>=0.9.11',
        'feedparser>=5.1.2',
        'lxml>=2.3.4',
	    'mysql-python>=1.2.3',
        'pycrypto>=2.6',
        'requests>=0.13.6',
        'setuptools>=0.6.21',
    ],
    tests_require=[
        'django-setuptest>=0.1.2',
    ],
    include_package_data=True,
)

if sys.argv[1] == 'install':
    '''
    Restore local_settings.py
    '''
    try:
        os.rename(TEMP_NAME, ORIG_NAME)
    except:
        pass
