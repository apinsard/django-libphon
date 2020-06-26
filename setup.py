# -*- coding: utf-8 -*-
import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-libphon',
    version='0.2',
    packages=['libphon'],
    include_package_data=True,
    license='MIT',
    description='Django app to handle some phone features',
    long_description=README,
    url='https://gitlab.com/cocoonr/django-libphon',
    author='Aladom & Cocoonr',
    author_email='contact@aladom.fr, contact@cocoonr.fr',
    install_requires=['phonenumbers'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independant',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
