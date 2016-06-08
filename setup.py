# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Zenodo - Research. Shared."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'mock>=1.3.0',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-flask>=0.10.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
    # 2.53.0 introduced a Python 3 compatibility issue. Wait for it to be fixed
    'selenium>=2.48.0,<2.53.0',
    'six>=1.10.0',
]

extras_require = {
    'docs': [
        'Sphinx>=1.4',
    ],
    'postgresql': [
        'invenio-db[postgresql,versioning]>=1.0.0a9',
    ],
    'mysql': [
        'invenio-db[mysql,versioning]>=1.0.0a9',
    ],
    'sqlite': [
        'invenio-db[versioning]>=1.0.0a9',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('postgresql', 'mysql', 'sqlite'):
        continue
    extras_require['all'].extend(reqs)

# Do not include in all requirement
extras_require['xrootd'] = [
    'xrootdpyfs>=0.1.1',
]

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=2.7.0',
]

install_requires = [
    'arrow>=0.7.0',
    'bleach>=1.4.3',
    'CairoSVG>=1.0.20',
    'datacite>=0.2.1',
    'dcxml>=0.1.0',
    'dojson>=1.2.1',
    'Flask==0.10.1',
    'Flask-BabelEx>=0.9.2',
    'Flask-Debugtoolbar>=0.10.0',
    'idutils>=0.2.0',
    'invenio-access>=1.0.0a5',
    'invenio-accounts>=1.0.0a10',
    'invenio-admin>=1.0.0a3',
    'invenio-assets>=1.0.0a4',
    'invenio-base>=1.0.0a11',
    'invenio-celery>=1.0.0a4',
    'invenio-communities>=1.0.0a6',
    'invenio-config>=1.0.0a1',
    'invenio-deposit>=1.0.0.dev20150000',
    'invenio-files-rest>=1.0.0a3',
    'invenio-formatter>=1.0.0a2',
    'invenio-i18n>=1.0.0a4',
    'invenio-indexer>=1.0.0a6',
    'invenio-jsonschemas>=1.0.0a3',
    'invenio-logging>=1.0.0a2',
    'invenio-mail>=1.0.0a3',
    'invenio-marc21>=1.0.0a2',
    'invenio-migrator>=1.0.0a5',
    'invenio-oaiserver>=1.0.0a5',
    'invenio-oauth2server>=1.0.0a5',
    'invenio-oauthclient>=1.0.0a2',
    'invenio-openaire>=1.0.0a3',
    'invenio-opendefinition>=1.0.0a2',
    'invenio-pages>=1.0.0a2',
    'invenio-pidstore>=1.0.0a7',
    'invenio-previewer>=1.0.0a4',
    'invenio-records-files>=1.0.0a6',
    'invenio-records-rest>=1.0.0a12',
    'invenio-records-ui>=1.0.0a6',
    'invenio-records>=1.0.0a16',
    'invenio-rest[cors]>=1.0.0a8',
    'invenio-search-ui>=1.0.0a4',
    'invenio-search>=1.0.0a7',
    'invenio-sipstore>=1.0.0a1',
    'invenio-theme>=1.0.0a10',
    'invenio-userprofiles>=1.0.0a5',
    'invenio-webhooks>=1.0.0a2',
    'jsonref>=0.1',
    'jsonresolver>=0.2.1',
    'marshmallow>=2.5.0',
    'Pillow>=3.2.0',
    'python-slugify>=1.2.0',
    'raven<=5.1.0',
    'wsgi-statsd>=0.3.1',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('zenodo', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='zenodo',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='zenodo research data repository',
    license='GPLv2',
    author='CERN',
    author_email='info@zenodo.org',
    url='https://github.com/zenodo/zenodo',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'zenodo = zenodo.cli:cli',
        ],
        'invenio_base.apps': [
            'zenodo_fixtures = zenodo.modules.fixtures:ZenodoFixtures',
            'zenodo_records = zenodo.modules.records.ext:ZenodoRecords',
            'zenodo_deposit = zenodo.modules.deposit.ext:ZenodoDeposit',
            'zenodo_xrootd = zenodo.modules.xrootd.ext:ZenodoXRootD',
            'zenodo_jsonschemas = '
            'zenodo.modules.jsonschemas.ext:ZenodoJSONSchemas',
            'flask_debugtoolbar = flask_debugtoolbar:DebugToolbarExtension',
        ],
        'invenio_base.api_apps': [
            'zenodo_xrootd = zenodo.modules.xrootd.ext:ZenodoXRootD',
        ],
        'invenio_base.blueprints': [
            'zenodo_deposit = zenodo.modules.deposit.views:blueprint',
            'zenodo_frontpage = zenodo.modules.frontpage.views:blueprint',
            'zenodo_search_ui = zenodo.modules.search_ui.views:blueprint',
            'zenodo_theme = zenodo.modules.theme.views:blueprint',
        ],
        'invenio_base.api_converters': [
            'file_key = zenodo.modules.deposit.utils:FileKeyConverter',
        ],
        'invenio_i18n.translations': [
            'messages = zenodo',
        ],
        'invenio_celery.tasks': [
            'zenodo_records = zenodo.modules.records.tasks',
        ],
        'invenio_pidstore.minters': [
            'zenodo_record_minter '
            '= zenodo.modules.records.minters:zenodo_record_minter',
            'zenodo_deposit_minter '
            '= zenodo.modules.deposit.minters:zenodo_deposit_minter',
        ],
        'invenio_pidstore.fetchers': [
            'zenodo_record_fetcher '
            '= zenodo.modules.records.fetchers:zenodo_record_fetcher',
            'zenodo_deposit_fetcher '
            '= zenodo.modules.deposit.fetchers:zenodo_deposit_fetcher'
        ],
        'invenio_assets.bundles': [
            'zenodo_theme_css = zenodo.modules.theme.bundles:css',
            'zenodo_theme_js = zenodo.modules.theme.bundles:js',
            'zenodo_search_js = zenodo.modules.theme.bundles:search_js',
        ],
        'invenio_jsonschemas.schemas': [
            'zenodo_records = zenodo.modules.records.jsonschemas',
            'zenodo_deposit = zenodo.modules.deposit.jsonschemas',
            'zenodo_sipstore = zenodo.modules.sipstore.jsonschemas',
        ],
        'invenio_search.mappings': [
            'records = zenodo.modules.records.mappings',
            'deposits = zenodo.modules.deposit.mappings',
        ],
        'dojson.contrib.to_marc21': [
            'zenodo = zenodo.modules.records.serializers.to_marc21.rules',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 3 - Alpha',
    ],
)
