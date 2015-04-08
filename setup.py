# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2012, 2013, 2014, 2015 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""
Zenodo - Research. Shared.

Links
-----

* `website <http://zenodo.org/>`_
* `development version <https://github.com/zenodo/zenodo>`_

"""

import os

from setuptools import find_packages, setup

install_requires = [
    "Invenio",
    "altmetric",
    "beautifulsoup4",
    "humanize",
    "github3.py>=0.9.0",
    "Pillow",
    "pyoai>=2.4.2",
    "awesome-slugify>=1.6",
]

extras_require = {
    "development": [
        "Flask-DebugToolbar==0.9.0",
        "kwalitee",
        "ipython",
        "ipdb",
    ]
}

tests_require = [
    "httpretty>=0.8.0",
    "Flask-Testing>=0.4.1",
    "mock",
    "nose",
    "selenium",
    "unittest2>=0.5.1",
]

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("zenodo", "version.py"), "rt") as fp:
    exec(fp.read(), g)
version = g["__version__"]


setup(
    name='zenodo',
    version=version,
    url='http://zenodo.org',
    license='GPLv3',
    author='CERN',
    author_email='info@zenodo.org',
    description='Research. Shared',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        'invenio.config': [
            "zenodo = zenodo.config"
        ]
    },
    test_suite='zenodo.testsuite.suite',
    tests_require=tests_require
)
