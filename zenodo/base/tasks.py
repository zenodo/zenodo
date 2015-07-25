# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from invenio.celery import celery


@celery.task
def doi_consistency_check():
    """Check if all DOIs in records have been registered."""
    from invenio.base.globals import cfg
    from invenio.modules.records.api import get_record
    from invenio.legacy.search_engine import perform_request_search
    from invenio.modules.pidstore.models import PersistentIdentifier
    from invenio.modules.pidstore.tasks import datacite_register

    result = perform_request_search(p="")
    for r in result:
        doi = get_record(r).get('doi')
        if doi and doi.startswith(cfg['CFG_DATACITE_DOI_PREFIX']):
            pid = PersistentIdentifier.get("doi", doi)
            if pid and pid.is_new():
                if pid.has_object("rec", r):
                    datacite_register.delay(r)
