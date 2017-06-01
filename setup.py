# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
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
    'check-manifest>=0.34',
    'coverage>=4.2',
    'isort>=4.2.2',
    'mock>=2.0.0',
    'pydocstyle>=1.1.1',
    'pytest-cache>=1.0',
    'pytest-cov>=2.4.0',
    'pytest-flask>=0.10.0',
    'pytest-pep8>=1.0.6',
    'pytest>=3.0.3',
    # 2.53.0 introduced a Python 3 compatibility issue. Wait for it to be fixed
    'selenium>=2.48.0,<2.53.0',
    'six>=1.10.0',
]

extras_require = {
    'docs': [
        'Sphinx>=1.4.2,<1.4.5',
    ],
    # Database version
    'postgresql': [
        'invenio-db[postgresql,versioning]>=1.0.0b3',
    ],
    'mysql': [
        'invenio-db[mysql,versioning]>=1.0.0b3',
    ],
    'sqlite': [
        'invenio-db[versioning]>=1.0.0b3',
    ],
    # Elasticsearch version
    'elasticsearch2': [
        'elasticsearch>=2.0.0,<3.0.0',
        'elasticsearch-dsl>=2.0.0,<3.0.0',
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
    'invenio-xrootd>=1.0.0a4',
    'xrootdpyfs>=0.1.3',
]

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=2.7.0',
]

install_requires = [
    'arrow>=0.8.0',
    'bleach>=1.5.0',
    'CairoSVG>=1.0.22,<2.0.0',
    'citeproc-py-styles>=0.1.0',
    'citeproc-py>=0.3.0',
    'datacite>=0.3.0',
    'dcxml>=0.1.0',
    'dojson>=1.2.1',
    'Flask>=0.11.1',
    'Flask-Admin>=1.4.2',
    'Flask-BabelEx>=0.9.3',
    'Flask-Cache>=0.13.1',
    'Flask-Debugtoolbar>=0.10.0',
    'Flask-Konch>=1.1.0',
    'ftfy>=4.2.0,<5',
    'idutils>=0.2.3',
    'invenio-access>=1.0.0a11',
    'invenio-accounts>=1.0.0b1',
    'invenio-admin>=1.0.0a3',
    'invenio-assets>=1.0.0b6',
    'invenio-base>=1.0.0a14',
    'invenio-celery>=1.0.0b1',
    'invenio-communities>=1.0.0a13',
    'invenio-config>=1.0.0b1',
    'invenio-csl-rest>=1.0.0a1',
    'invenio-deposit>=1.0.0a8',
    'invenio-files-rest>=1.0.0a14.post2',
    'invenio-formatter>=1.0.0a2',
    'invenio-github>=1.0.0a10',
    'invenio-i18n>=1.0.0b1',
    'invenio-indexer>=1.0.0a8',
    'invenio-jsonschemas>=1.0.0a3',
    'invenio-logging>=1.0.0a3',
    'invenio-mail>=1.0.0a5',
    'invenio-marc21>=1.0.0a3',
    'invenio-migrator>=1.0.0a8',
    'invenio-oaiserver>=1.0.0a12',
    'invenio-oauth2server>=1.0.0a14',
    'invenio-oauthclient[github]>=1.0.0a12',
    'invenio-openaire>=1.0.0a7',
    'invenio-opendefinition>=1.0.0a3',
    'invenio-pages>=1.0.0a3',
    'invenio-pidstore>=1.0.0b1',
    'invenio-pidrelations>=1.0.0a3',
    'invenio-previewer>=1.0.0a10',
    'invenio-records>=1.0.0b1',
    'invenio-records-files>=1.0.0a8',
    'invenio-records-rest>=1.0.0a17',
    'invenio-records-ui>=1.0.0a8',
    'invenio-rest[cors]>=1.0.0a10',
    'invenio-search>=1.0.0a9',
    'invenio-search-ui>=1.0.0a5',
    'invenio-sipstore>=1.0.0a3',
    'invenio-theme>=1.0.0a14',
    'invenio-userprofiles>=1.0.0a9',
    'invenio-webhooks>=1.0.0a4',
    'jsonref>=0.1',
    'jsonresolver>=0.2.1',
    'marshmallow==2.13.4',
    'Pillow>=3.4.2',
    'python-slugify>=1.2.1',
    'raven<=5.1.0',
    'sickle>=0.6.1',
    'uwsgi>=2.0.14',
    'uwsgitop>=0.9',
    'wsgi-statsd>=0.3.1',
    'zenodo-accessrequests>=1.0.0a2',
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
            'zenodo_auditor = zenodo.modules.auditor.ext:ZenodoAuditor',
            'zenodo_cache = zenodo.modules.cache.ext:ZenodoCache',
            'zenodo_fixtures = zenodo.modules.fixtures.ext:ZenodoFixtures',
            'zenodo_records = zenodo.modules.records.ext:ZenodoRecords',
            'zenodo_deposit = zenodo.modules.deposit.ext:ZenodoDeposit',
            'zenodo_xrootd = zenodo.modules.xrootd.ext:ZenodoXRootD',
            'zenodo_jsonschemas = '
            'zenodo.modules.jsonschemas.ext:ZenodoJSONSchemas',
            'flask_debugtoolbar = flask_debugtoolbar:DebugToolbarExtension',
        ],
        'invenio_base.api_apps': [
            'zenodo_cache = zenodo.modules.cache.ext:ZenodoCache',
            'zenodo_deposit = zenodo.modules.deposit.ext:ZenodoDeposit',
            'zenodo_records = zenodo.modules.records.ext:ZenodoRecords',
            'zenodo_xrootd = zenodo.modules.xrootd.ext:ZenodoXRootD',
        ],
        'invenio_base.blueprints': [
            'zenodo_communities = zenodo.modules.communities.views:blueprint',
            'zenodo_deposit = zenodo.modules.deposit.views:blueprint',
            'zenodo_frontpage = zenodo.modules.frontpage.views:blueprint',
            'zenodo_openaire = zenodo.modules.openaire.views:blueprint',
            'zenodo_redirector = zenodo.modules.redirector.views:blueprint',
            'zenodo_search_ui = zenodo.modules.search_ui.views:blueprint',
            'zenodo_theme = zenodo.modules.theme.views:blueprint',
        ],
        'invenio_base.api_blueprints': [
            'zenodo_rest = zenodo.modules.rest.views:blueprint',
        ],
        'invenio_base.api_converters': [
            'file_key = zenodo.modules.deposit.utils:FileKeyConverter',
        ],
        'invenio_i18n.translations': [
            'messages = zenodo',
        ],
        'invenio_celery.tasks': [
            'zenodo_auditor = zenodo.modules.auditor.tasks',
            'zenodo_records = zenodo.modules.records.tasks',
            'zenodo_utils = zenodo.modules.utils.tasks',
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
            '= zenodo.modules.deposit.fetchers:zenodo_deposit_fetcher',
            'zenodo_doi_fetcher '
            '= zenodo.modules.records.fetchers:zenodo_doi_fetcher',
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
        'Programming Language :: Python :: 3.5',
        'Development Status :: 3 - Alpha',
    ],
)
