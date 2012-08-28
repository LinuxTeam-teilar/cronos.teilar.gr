#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='cronos',
    version='0.3-dev',
    description='Django application that collects announcements and other \
personal data for students of TEI of Larissa',
    author='cronos development team',
    author_email='cronos@teilar.gr',
    url='http://cronos.teilar.gr',
    packages=find_packages(),
    include_package_data=True
)
