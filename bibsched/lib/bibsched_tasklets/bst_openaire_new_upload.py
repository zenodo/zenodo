#!/usr/bin/env python
## This file is part of Invenio.
## Copyright (C) 2010, 2011, 2012 CERN.
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

"""
Simple tasklet that is called after a bibupload of a new record
"""

from invenio.flaskshell import *
from invenio.openaire_tasks import openaire_create_icon, \
    openaire_altmetric_update, openaire_register_doi, \
    openaire_upload_notification


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

if __name__ == '__main__':
    bst_openaire_new_upload()
