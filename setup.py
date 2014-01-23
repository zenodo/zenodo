# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""
ZENODO - Research. Shared.
"""

from setuptools import setup, find_packages
import os


def requirements():
    req = []
    dep = []
    for filename in ['requirements.txt']:
        with open(os.path.join(os.path.dirname(__file__), filename), 'r') as f:
            for line in f.readlines():
                if line.startswith('#'):
                    continue
                if '://' in line:
                    dep.append(str(line[:-1]))
                else:
                    req.append(str(line))
    return req, dep

install_requires, dependency_links = requirements()

setup(
    name='zenodo',
    version='dev',
    url='http://zenodo.org',
    license='GPLv3',
    author='CERN',
    author_email='info@zenodo.org',
    description='Research. Shared',
    long_description=__doc__,
    packages=find_packages(),
    namespace_packages=['zenodo', 'zenodo.ext', 'zenodo.modules', ],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    dependency_links=dependency_links,
    entry_points={
        'invenio.config': [
            "zenodo = zenodo.config"
        ]
    },
    test_suite='zenodo.testsuite.suite'
)
