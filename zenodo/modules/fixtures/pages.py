# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Pages fixtures for Zenodo."""

from __future__ import absolute_import, print_function

from os.path import join

from invenio_db import db
from invenio_pages.models import Page

from .utils import file_stream, read_json


def loadpages(force=False):
    """Load pages."""
    data = read_json('data/pages.json')

    try:
        if force:
            Page.query.delete()
        for p in data:
            if len(p['description']) >= 200:
                raise ValueError(  # pragma: nocover
                    "Description too long for {0}".format(p['url']))
            p = Page(
                url=p['url'],
                title=p['title'],
                description=p['description'],
                content=file_stream(
                    join('data', p['file'])).read().decode('utf8'),
                template_name=p['template_name'],
            )
            db.session.add(p)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
