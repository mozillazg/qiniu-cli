#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
import sys
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import qiniu_cli

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

packages = [
    'qiniu_cli',
]

requirements = [
    'Click',
    'requests',
]


def long_description():
    readme = open('README.rst', encoding='utf8').read()
    text = readme + '\n\n' + open('CHANGELOG.rst', encoding='utf8').read()
    return text

setup(
    name=qiniu_cli.__title__,
    version=qiniu_cli.__version__,
    description=qiniu_cli.__doc__,
    long_description=long_description(),
    url='https://github.com/mozillazg/qiniu-cli',
    author=qiniu_cli.__author__,
    author_email='mozillazg101@gmail.com',
    license=qiniu_cli.__license__,
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'qiniu_cli': 'qiniu_cli'},
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'qiniu_cli = qiniu_cli.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Environment :: Console',
        'Topic :: Utilities',
        'Topic :: Terminals',
    ],
    keywords='Qiniu, CLI',
)
