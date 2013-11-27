# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA


from invenio.dbquery import run_sql
from invenio.config import CFG_DATACITE_DOI_PREFIX


def create_doi(recid=None):
    """ Generate a new DOI """
    if recid is None:
        recid = run_sql("INSERT INTO bibrec (creation_date, modification_date)"
                        " VALUES (NOW(), NOW())")

    return dict(
        doi='%s/zenodo.%s' % (CFG_DATACITE_DOI_PREFIX, recid),
        recid=recid,
    )


def filter_empty_helper(keys=None):
    """ Remove empty elements from a list"""
    def _inner(elem):
        if isinstance(elem, dict):
            for k, v in elem.items():
                if (keys is None or k in keys) and v:
                    return True
            return False
        else:
            return bool(elem)
    return _inner
