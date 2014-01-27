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

from invenio.legacy.dbquery import run_sql


depends_on = ['openaire_2013_03_11_zenodo_user']


def info():
    return "Set content-type for DataCite output format"


def do_upgrade():
    """ Implement your upgrades here  """
    res = run_sql("SELECT id FROM format WHERE code='da'")
    if res:
        run_sql("""UPDATE format SET code='dcite', content_type="text/xml", name="DataCite", visibility=1, description="DataCite XML Metadata Kernel" WHERE code='da'""")
    else:
        run_sql("""INSERT INTO format (content_type, name, visibility, description, code) VALUES ("text/xml", "DataCite", 1, "DataCite XML Metadata Kernel", 'dcite')""")


def estimate():
    """  Estimate running time of upgrade in seconds (optional). """
    return 1
