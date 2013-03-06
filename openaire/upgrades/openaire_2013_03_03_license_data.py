# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import warnings
from invenio.dbquery import run_sql
from invenio.textutils import wait_for_user


depends_on = ['openaire_2013_02_18_zenodo_data']


def info():
    return "Install license data into knowledge base"


def do_upgrade():
    """ Install license data into knowledge base """
    import requests
    import json

    r = requests.get('http://licenses.opendefinition.org/licenses/groups/all.json')
    if r.status_code != 200:
        raise RuntimeError("Couldn't download http://licenses.opendefinition.org/licenses/groups/all.json")
    licenses = json.loads(r.text)

    res = run_sql("INSERT INTO knwKB (name,description,kbtype) VALUES ('licenses','','w')")
    for key, value in licenses.items():
        run_sql("INSERT INTO knwKBRVAL (m_key,m_value,id_knwKB) VALUES (%s,%s,%s)", (key, json.dumps(value), res))


def estimate():
    """  Estimate running time of upgrade in seconds (optional). """
    return 5

def pre_upgrade():
    """  Run pre-upgrade checks (optional). """
    try:
        import requests
    except ImportError:
        raise RuntimeError("Python package requests not installed. Please install to continue.")
