# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2012, 2013 CERN.
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

"""
Simple tasklet that is called after a bibupload of a new record
"""

from zenodo.modules.deposit.tasks import openaire_create_icon, \
    openaire_altmetric_update, openaire_register_doi, \
    openaire_upload_notification
from zenodo.modules.preservationmeter.tasks import calculate_preservation_score


def bst_openaire_new_upload(recid=None):
    """
    Tasklet to run after a new record has been uploaded.
    """
    if recid is None:
        return

    # Ship of tasks to Celery for background processing
    openaire_register_doi.delay(recid=recid)
    openaire_create_icon.delay(recid=recid)
    openaire_altmetric_update.delay([recid])
    openaire_upload_notification.delay(recid=recid)
    calculate_preservation_score.delay(recid=recid)

if __name__ == '__main__':
    bst_openaire_new_upload()
