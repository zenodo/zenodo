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
Zenodo configuration
--------------------
Instance independent configuration (e.g. which extensions to load) is defined
in ``zenodo.config'' while instance dependent configuration (e.g. database
host etc.) is defined in an optional ``zenodo.instance_config'' which
can be installed by a separate package.

This config module is loaded by the Flask application factory via an entry
point specified in the setup.py::

    entry_points={
        'invenio.config': [
            "zenodo = zenodo.config"
        ]
    },
"""

PACKAGES = [
    'zenodo.base',
    #'zenodo.modules.*',
    'invenio.modules.*',
]

# Default database name
CFG_DATABASE_NAME = "zenodo"
CFG_DATABASE_USER = "zenodo"

try:
    from zenodo.instance_config import *
except ImportError:
    pass
