#!/usr/bin/env python
"""
sentry-zulip
============

An extension for `Sentry <https://getsentry.com>`_ which posts notifications
to `Zulip <https://www.zulip.org>`_.

:copyright: (c) 2015 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from setuptools import setup, find_packages


install_requires = [
    'sentry>=7.0.0',
]

tests_require = [
    'exam',
    'flake8>=2.0,<2.1',
    'responses',
]

setup(
    name='sentry-zulip',
    version='0.6.0.dev0',
    author='Matt Robenolt',
    author_email='matt@ydekproductons.com',
    # url='https://github.com/getsentry/sentry-zulip',
    description='A Sentry extension which posts notifications to Zulip (https://www.zulip.org/).',
    long_description=open('README.rst').read(),
    license='BSD',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'tests': tests_require,
    },
    include_package_data=True,
    entry_points={
        'sentry.apps': [
            'zulip = sentry_zulip',
        ],
        'sentry.plugins': [
            'zulip = sentry_zulip.plugin:ZulipPlugin',
        ]
    },
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
