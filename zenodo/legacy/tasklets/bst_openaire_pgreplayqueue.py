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

from marshal import loads
from zlib import decompress

from invenio.legacy.dbquery import run_sql
from zenodo.legacy.utils.dnetutils import dnet_run_sql
from invenio.errorlib import register_exception
from intbitset import intbitset


def bst_openaire_pgreplayqueue():
    """
    Execute a failed D-NET query.

    See invenio.dnetutils.dnet_save_query_into_pgreplayqueue for further info.
    """
    replayqueue = intbitset(run_sql("SELECT id FROM pgreplayqueue"))
    for queryid in replayqueue:
        query, param = loads(decompress(run_sql("SELECT query FROM pgreplayqueue WHERE id=%s", (queryid, ))[0][0]))
        try:
            dnet_run_sql(query, param, support_replay=False)
        except:
            ## Mmh... things are still not working. Better give up now!
            try:
                run_sql("UPDATE pgreplayqueue SET last_try=NOW() WHERE id=%s", (queryid, ))
            except:
                register_exception(alert_admin=True)
                ## We are not really interested in this particular error.
                pass
            raise
        else:
            run_sql("DELETE FROM pgreplayqueue WHERE id=%s", (queryid, ))
