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

import warnings
from invenio.legacy.dbquery import run_sql
from invenio.ext.sqlalchemy import db
from datetime import datetime
import os
import json
import logging

depends_on = ['openaire_2013_09_25_software_coll']

from invenio.modules.knowledge.api import get_kb_mapping



class OldDeposition(object):
    def __init__(self, pubid, prjid, uid, recid):
        self.id = pubid
        self.recid = recid
        self.user_id = uid
        self.prjid = prjid

    def get_marcxml(self):
        from invenio.config import CFG_WEBSUBMIT_STORAGEDIR
        xml_file = os.path.join(
            CFG_WEBSUBMIT_STORAGEDIR, 'small',
            str(self.user_id), str(self.id), 'marcxml'
        )
        return open(xml_file, 'r').read()

    def get_metadata(self):
        from invenio.config import CFG_WEBSUBMIT_STORAGEDIR
        metadata_file = os.path.join(
            CFG_WEBSUBMIT_STORAGEDIR, 'small',
            str(self.user_id), str(self.id), 'metadata'
        )

        return json.load(open(metadata_file))

    def get_files(self):
        from invenio.config import CFG_WEBSUBMIT_STORAGEDIR
        small = os.path.join(CFG_WEBSUBMIT_STORAGEDIR, 'small',
                             str(self.user_id), str(self.id), 'files')
        large = os.path.join(CFG_WEBSUBMIT_STORAGEDIR, 'large',
                             str(self.user_id), str(self.id), 'files')

        files = {}

        for p in [small, large]:
            for d in os.listdir(p):
                if not d.startswith('.') and os.path.isdir(os.path.join(p, d)):
                    for f in os.listdir(os.path.join(p, d)):
                        if not f.startswith('.'):
                            files[d] = os.path.join(p, d, f)

        return files


def map_metadata(metadata):
    from werkzeug.datastructures import MultiDict
    from invenio.modules.communities.models import Community
    newdata = metadata.copy()

    del_keys = [
        '__form__', '__cd__', '__md__', '__publicationid__',
        '__status__', '__uid__',
    ]

    for k in del_keys:
        try:
            del newdata[k]
        except Exception:
            pass

    if '__doi__' in newdata:
        newdata['prereserve_doi'] = {'doi': newdata['__doi__'], 'recid': newdata['__recid__']}
        newdata['recid'] = newdata['__recid__']
        del newdata['__doi__']
        del newdata['__recid__']
    elif '__recid__' in metadata:
        newdata['recid'] = newdata['__recid__']
        del newdata['__recid__']

    if 'creators' in newdata:
        newdata['creators'] = map(lambda x: {'name': x[0], 'affiliation': x[1]}, newdata['creators'])

    if 'thesis_supervisors' in newdata:
        newdata['thesis_supervisors'] = map(lambda x: {'name': x[0], 'affiliation': x[1]}, newdata['thesis_supervisors'])

    if 'related_identifiers' in newdata:
        newdata['related_identifiers'] = map(lambda x: {'scheme': 'doi', 'identifier': x, 'relation': 'isReferencedBy'}, newdata['related_identifiers'])

    if 'funding_source' in newdata:
        def _f1(x):
            info = get_kb_mapping('json_projects', str(x))
            data = json.loads(info['value'])
            return {'id': x, 'title': data.get('title', ''), 'acronym': data.get('acronym', '')}
        newdata['grants'] = map(_f1, newdata['funding_source'])
        del newdata['funding_source']

    if 'collections' in newdata:
        def _f2(x):
            u = Community.query.filter_by(id=x).first()
            return {'identifier': u.id, 'title': u.title}
        newdata['communities'] = map(_f2, newdata['collections'])
        del newdata['collections']

    return MultiDict(newdata)


def info():
    return "Upgrade to new webdeposit infrastructure"


def do_upgrade():
    """ Implement your upgrades here  """
    #run_sql("DELETE FROM bwlOBJECT")
    #run_sql("DELETE FROM bwlOBJECTLOGGING")
    #run_sql("DELETE FROM bwlWORKFLOW")
    #run_sql("DELETE FROM bwlWORKFLOWLOGGING")
    #os.system("rm -Rf /home/lnielsen/envs/zenodonext/var/data/deposit/storage/*")

    logger = logging.getLogger('invenio_upgrader')
    from invenio.webdeposit_models import Deposition, DepositionDraft, \
        DepositionType, DepositionFile
    from invenio.webdeposit_storage import DepositionStorage
    from invenio.webdeposit_load_forms import forms
    from invenio.bibworkflow_config import CFG_OBJECT_VERSION, CFG_WORKFLOW_STATUS

    default_type = DepositionType.get_default()


    for row in run_sql("SELECT publicationid, projectid, uid, id_bibrec FROM eupublication"):
        try:
            logger.info("Migrating publication id %s from user %s..." % (row[0], row[2]))
            old = OldDeposition(*row)
            dep = Deposition(None, user_id=old.user_id)

            # Add files
            backend = DepositionStorage(dep.id)
            for f in old.get_files().values():
                 fp = open(f, 'r')
                 df = DepositionFile(backend=backend)
                 df.save(fp, filename=os.path.basename(f))
                 fp.close()
                 dep.add_file(df)

            metadata = old.get_metadata()
            is_submitted = metadata['__status__'] == 'submitted'
            modified = datetime.fromtimestamp(metadata['__md__'])
            created = datetime.fromtimestamp(metadata['__cd__'])

            dep.workflow_object.created = created
            dep.workflow_object.modified = modified

            # Add draftg
            draft = dep.get_or_create_draft('_default', form_class=forms['ZenodoForm'])
            draft.validate = True

            m = map_metadata(metadata)
            recid = m.get('recid', None)
            draft.process(m, complete_form=True)

            if is_submitted:
                if not recid:
                    raise RuntimeError("Something is wrong")
                draft.completed = True
                dep.workflow_object.version = CFG_OBJECT_VERSION.FINAL

                sip = dep.create_sip()
                sip.metadata['recid'] = recid

                sip.metadata['fft'] = sip.metadata['files']
                del sip.metadata['files']

                sip.package = old.get_marcxml()
                sip.seal()

            dep.save()

            dep.workflow_object.created = created
            dep.workflow_object.modified = modified

            db.session.add(dep.workflow_object)
            db.session.commit()
        except Exception, e:
            import traceback
            warnings.warn("Failed to migrate %s (from user %s): %s" % (row[0], row[2], traceback.format_exc(e)))


    #raise RuntimeError("Failed")


def estimate():
    """  Estimate running time of upgrade in seconds (optional). """
    return 10
