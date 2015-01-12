# -*- coding: utf-8 -*-
##
## This file is part of Zenodo.
## Copyright (C) 2014 CERN.
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


from sqlalchemy import *
import logging


depends_on = [
    u'zenodo_2014_03_18_hstrecord_autoincrement',
    u'oauth2server_2014_10_21_encrypted_token_columns',
    u'oauthclient_2014_10_21_encrypted_token_column',
]
logger = logging.getLogger('invenio_upgrader')


def info():
    return "Fix issues in workflow objects with task counter and default data."


def _get_state(d):
    s = d.state
    if s == 'inprogress':
        if len(d.sips) > 0:
            if not d.sips[-1].is_sealed():
                print "Look at {}".format(d.workflow_object.id)
            return "inprogress-edit"
        else:
            return "inprogress-new"
    else:
        return s


def do_upgrade():
    """Implement your upgrades here."""
    from invenio.modules.workflows.models import BibWorkflowObject
    from invenio.modules.deposit.models import Deposition

    q = BibWorkflowObject.query.filter(BibWorkflowObject.id_user != 0).all()
    for b in q:
        try:
            d = Deposition(b)
        except KeyError:
            logger.info("Fixing data in {}".format(b.id))
            b.set_data(dict(
                type='upload',
                title='Untitled',
                files=[],
                drafts={},
                sips=[],
            ))
            d = Deposition(b)
            d.save()

        s = _get_state(d)
        c = str(b.get_extra_data().get('_task_counter'))
        co = str(b.get_extra_data().get('task_counter'))

        if s == 'inprogress-new':
            if c == "[0, 0, 3, 1]":
                b.save(task_counter=[0, 3, 1])
            elif c == "[0, 0, 3, 2]":
                b.save(task_counter=[0, 3, 2])
            elif c == "None" and co == "[0, 0, 3, 1]":
                b.save(task_counter=[0, 3, 1])
        elif s == 'inprogress-edit':
            if c == "[0, 0, 1, 0]":
                b.save(task_counter=[0, 1, 0])
            elif c == "[0, 0, 1, 1]":
                b.save(task_counter=[0, 1, 1])
            elif c == "[0, 4, 3, 0]":
                b.save(task_counter=[4, 3, 0])
            elif c == "None" and co == "[0, 0, 1, 1]":
                b.save(task_counter=[0, 1, 1])
            elif c == "None" and co == "[0, 0, 1, 0]":
                b.save(task_counter=[0, 1, 0])
            elif b.id == 2076:
                b.save(task_counter=[4, 3, 0])
                b.workflow.save(status=4)
        elif s == 'error':
            if c == "[0, 0, 1, 0]":
                b.save(task_counter=[0, 1, 0])
            elif c == "[0, 0, 1, 1]":
                b.save(task_counter=[0, 1, 1])
            elif c == "[0, 0, 3, 1]":
                b.save(task_counter=[0, 3, 1])
            elif c == "[0, 0, 3, 2]":
                b.save(task_counter=[0, 3, 2])
            elif c == "[0, 4, 3, 0]":
                b.save(task_counter=[4, 3, 0])
            elif c == "[0, 4, 3, 1]":
                b.save(task_counter=[4, 3, 1])


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1
