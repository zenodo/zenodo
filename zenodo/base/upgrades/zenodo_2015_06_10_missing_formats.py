# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from sqlalchemy import *
from invenio.ext.sqlalchemy import db

depends_on = [u'zenodo_2015_03_04_firerole_email_to_uid']


def info():
    return "Add missing formats to database."


def do_upgrade():
    """Implement your upgrades here."""
    from invenio.modules.formatter.models import Format
    from invenio.modules.formatter.registry import output_formats_lookup

    for name in output_formats_lookup.keys():
        if name.endswith(".bfo"):
            code = name.lower()[:-4]
            try:
                Format.query.filter_by(code=code).one()
            except Exception:
                f = Format(name=code, code=code, description="",
                           content_type="", visibility=0, mime_type=None)
                db.session.add(f)

    db.session.commit()


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1


def pre_upgrade():
    """Run pre-upgrade checks (optional)."""
    # Example of raising errors:
    # raise RuntimeError("Description of error 1", "Description of error 2")


def post_upgrade():
    """Run post-upgrade checks (optional)."""
    # Example of issuing warnings:
    # warnings.warn("A continuable error occurred")
