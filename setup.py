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
        'Sphinx>=1.3',
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

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=2.7.0',
]

install_requires = [
    'CairoSVG>=1.0.20',
    'datacite>=0.2.1',
    'dcxml>=0.1.0',
    'dojson>=1.0.0',
    'Flask-BabelEx>=0.9.2',
    'Flask-Debugtoolbar>=0.10.0',
    'idutils>=0.2.0',
    'invenio-access',
    'invenio-accounts',
    'invenio-admin',
    'invenio-assets',
    'invenio-base',
    'invenio-celery',
    'invenio-config',
    'invenio-deposit',
    'invenio-files-rest',
    'invenio-formatter',
    'invenio-i18n',
    'invenio-jsonschemas',
    'invenio-logging',
    'invenio-mail',
    'invenio-marc21',
    'invenio-migrator',
    'invenio-oauth2server',
    'invenio-oauthclient',
    'invenio-openaire',
    'invenio-opendefinition',
    'invenio-pages',
    'invenio-pidstore',
    'invenio-previewer',
    'invenio-records',
    'invenio-records-rest',
    'invenio-records-ui',
    'invenio-rest[cors]',
    'invenio-search',
    'invenio-theme',
    'invenio-userprofiles',
    'jsonref>=0.1',
    'marshmallow>=2.5.0',
    'Pillow>=3.2.0',
    'python-slugify>=1.2.0',
    'zenodo-migrationkit>=1.0.0.dev20150000',
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
            'flask_debugtoolbar = flask_debugtoolbar:DebugToolbarExtension',
        ],
        'invenio_base.api_apps': [
            'invenio_records = invenio_records:InvenioRecords',
        ],
        'invenio_base.blueprints': [
            'zenodo_frontpage = zenodo.modules.frontpage.views:blueprint',
            'zenodo_search_ui = zenodo.modules.search_ui.views:blueprint',
            'zenodo_theme = zenodo.modules.theme.views:blueprint',
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
        ],
        'invenio_pidstore.fetchers': [
            'zenodo_record_fetcher '
            '= zenodo.modules.records.fetchers:zenodo_record_fetcher',
        ],
        'invenio_assets.bundles': [
            'zenodo_theme_css = zenodo.modules.theme.bundles:css',
            'zenodo_theme_js = zenodo.modules.theme.bundles:js',
        ],
        'invenio_jsonschemas.schemas': [
            'zenodo_records = zenodo.modules.records.jsonschemas',
        ],
        'invenio_search.mappings': [
            'records = zenodo.modules.records.mappings',
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
