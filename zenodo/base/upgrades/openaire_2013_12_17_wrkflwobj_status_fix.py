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

from invenio.legacy.dbquery import run_sql


depends_on = ['openaire_2013_10_11_webdeposit_migration']


def info():
    return "Fix status issue in workflow and workflow objects"


def do_upgrade():
    from invenio.bibworkflow_model import BibWorkflowObject
    from invenio.webdeposit_models import Deposition

    ids = []
    ids_wf = []

    for b in BibWorkflowObject.query.all():
        d = Deposition.get(b.id)
        if d.submitted and (d.workflow_object.version != 1 or
           d.workflow_object.workflow.status != 5):
            ids.append(b.id)
            ids_wf.append(d.workflow_object.id_workflow)

    ids = ", ".join(str(o) for o in ids)
    ids_wf = ", ".join("'%s'" % o for o in ids_wf)

    run_sql("UPDATE bwlOBJECT SET version=1 WHERE id in (%s)" % ids)
    run_sql("UPDATE bwlWORKFLOW SET status=5 WHERE uuid in (%s)" % ids_wf)


def estimate():
    """  Estimate running time of upgrade in seconds (optional). """
    return 5
