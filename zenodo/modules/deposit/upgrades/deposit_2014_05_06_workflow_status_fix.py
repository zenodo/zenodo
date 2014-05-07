# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
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
from sqlalchemy import *
from invenio.ext.sqlalchemy import db


depends_on = []


def is_done(d):
    if len(d.sips) > 0 and d.sips[-1].is_sealed():
        if len(d.drafts.keys()) == 0:
            return True
        if len(d.drafts.keys()) == 1:
            if '_default' in d.drafts and d.drafts['_default'].is_completed():
                return True
            elif '_edit' in d.drafts and (
                 not d.drafts['_edit'] or d.drafts['_edit'].is_completed()):
                return True
        else:
            return True
    return False


def is_error(d):
    from invenio.modules.workflows.engine import WorkflowStatus
    return d.workflow_object.workflow and \
        d.workflow_object.workflow.status == WorkflowStatus.ERROR


def is_inprogress(d):
    return is_submitted(d) or is_unsubmitted(d)


def is_submitted(d):
    return len(d.sips) > 0 and len(d.drafts.keys()) > 0


def is_unsubmitted(d):
    return len(d.sips) == 0 and (
        '_default' in d.drafts or len(d.drafts.keys()) == 0
    )


def warn(o, state, msg):
    global bad
    bad += 1
    warnings.warn("Fix id %s state %s: %s" % (o.id, state, msg))


def info_msg(o, state):
    global good
    good += 1
    warnings.warn("OK id %s state %s: %s/%s" % (
        o.id,
        state,
        o.version,
        o.workflow.status if o.workflow else None
    ))


def info():
    return "Fix version/status issues in workflows"

good = 0
bad = 0

def do_upgrade():
    """ Implement your upgrades here  """
    from invenio.modules.workflows.models import BibWorkflowObject
    from invenio.modules.workflows.engine import ObjectVersion, WorkflowStatus
    from invenio.modules.deposit.models import Deposition

    for o in BibWorkflowObject.query.filter(BibWorkflowObject.id_user!=0).all():
        d = Deposition(o)
        if is_error(d):
            warn(o, 'ERROR', "run workflow")
            sip = d.get_latest_sip(sealed=False)
            for k in ['first_author', 'additional_authors']:
                if k in sip.metadata:
                    sip.metadata['_%s' % k] = sip.metadata[k]
                    del sip.metadata[k]
            d.run_workflow(headless=True)
        elif is_done(d):
            if o.version != ObjectVersion.FINAL or o.workflow.status != WorkflowStatus.COMPLETED:
                if o.version == ObjectVersion.HALTED and o.workflow.status == ObjectVersion.HALTED:
                    warn(o, 'DONE', "wf status %s -> %s" % (o.workflow.status, WorkflowStatus.COMPLETED))
                    warn(o, 'DONE', "obj version %s -> %s" % (o.version, ObjectVersion.FINAL))
                    o.workflow.status = WorkflowStatus.COMPLETED
                    o.version = ObjectVersion.FINAL
                elif o.version == ObjectVersion.FINAL and o.workflow.status == 5:
                    warn(o, 'DONE', "wf status %s -> %s" % (o.workflow.status, WorkflowStatus.COMPLETED))
                    o.workflow.status = WorkflowStatus.COMPLETED
                elif o.version == ObjectVersion.HALTED and o.workflow.status == WorkflowStatus.COMPLETED:
                    warn(o, 'DONE', "obj version %s -> %s" % (o.version, ObjectVersion.FINAL))
                    o.version = ObjectVersion.FINAL
                else:
                    warn(o, 'DONE', "Unmatched version %s status %s" % (o.version, o.workflow.status if o.workflow else None))
            else:
                info_msg(o, 'DONE')
        elif is_inprogress(d):
            if is_submitted(d):
                if o.version == ObjectVersion.HALTED and o.workflow.status == WorkflowStatus.HALTED:
                    info_msg(o, 'INPROGRESS/SUBMITTED')
                elif o.version == ObjectVersion.INITIAL and o.workflow.status == WorkflowStatus.NEW:
                    info_msg(o, 'INPROGRESS/SUBMITTED')
                elif o.version == ObjectVersion.HALTED and o.workflow.status == WorkflowStatus.COMPLETED:
                    warn(o, 'INPROGRESS/SUBMITTED', "wf status %s -> %s" % (o.workflow.status, WorkflowStatus.HALTED))
                    o.workflow.status = WorkflowStatus.HALTED
                else:
                    warn(o, 'INPROGRESS/SUBMITTED', "Unmatched version %s status %s" % (o.version, o.workflow.status if o.workflow else None))
            elif is_unsubmitted(d):
                if o.workflow is None:
                    if o.version != ObjectVersion.INITIAL:
                        warn(o, 'INPROGRESS/UNSUBMITTED', "Unmatched version %s status %s" % (o.version, o.workflow.status if o.workflow else None))
                    else:
                        info_msg(o, 'INPROGRESS/UNSUBMITTED')
                elif o.version == ObjectVersion.HALTED and o.workflow.status == WorkflowStatus.HALTED:
                    info_msg(o, 'INPROGRESS/UNSUBMITTED')
                elif o.version == ObjectVersion.HALTED and o.workflow.status == WorkflowStatus.RUNNING:
                    warn(o, 'INPROGRESS/UNSUBMITTED', "wf status %s -> %s" % (o.workflow.status, WorkflowStatus.HALTED))
                    o.workflow.status = WorkflowStatus.HALTED
                elif o.version == ObjectVersion.RUNNING and o.workflow.status == WorkflowStatus.RUNNING:
                    warn(o, 'INPROGRESS/UNSUBMITTED', "wf status %s -> %s" % (o.workflow.status, WorkflowStatus.HALTED))
                    warn(o, 'INPROGRESS/UNSUBMITTED', "obj version %s -> %s" % (o.version, ObjectVersion.HALTED))
                    o.version = ObjectVersion.HALTED
                    o.workflow.status = WorkflowStatus.HALTED
                elif o.version == ObjectVersion.HALTED and o.workflow.status == WorkflowStatus.COMPLETED:
                    warn(o, 'INPROGRESS/UNSUBMITTED', "wf status %s -> %s" % (o.workflow.status, WorkflowStatus.HALTED))
                    o.workflow.status = WorkflowStatus.HALTED
                else:
                    warn(o, 'INPROGRESS/UNSUBMITTED', "Unmatched version %s status %s" % (o.version, o.workflow.status if o.workflow else None))
            else:
                warn(o, 'INPROGRESS/?', "Unmatched version %s status %s" % (o.version, o.workflow.status if o.workflow else None))
    global good, bad
    warnings.warn("Good: %s Bad: %s" % (good, bad))
    db.session.commit()


def estimate():
    """  Estimate running time of upgrade in seconds (optional). """
    return 5
