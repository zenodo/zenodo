# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2015 CERN.
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
from invenio.modules.upgrader.api import op
from invenio.utils.text import wait_for_user
import time

depends_on = [u'zenodo_2015_02_24_orcid_userext']


def info():
    return "Migrate fireroles from email to uid."


def do_upgrade():
    """Implement your upgrades here."""
    from invenio.modules.accounts.models import User
    from invenio.modules.editor.models import Bibdoc
    from invenio.modules.access.firerole import compile_role_definition

    # Update fireroles.
    Bibdoc.query.filter_by(status='firerole: allow any').update(
        dict(status='')
    )

    # Migrate from email to uid.
    updates = []
    for d in Bibdoc.query.filter(Bibdoc.status.like("firerole:%")):
        firerole = d.status[len("firerole:"):].strip()
        default_p, roles = compile_role_definition(firerole)
        lines = []
        for allow_p, not_p, field, exp in roles:
            line = []
            line.append("allow" if allow_p else "deny")
            if not_p:
                line.append("not")

            # Rewrite from email into using uid.
            if field == 'email' and len(exp) == 1:
                email = exp[0][1]
                try:
                    u = User.query.filter_by(email=email).one()
                    line.append('uid')
                    line.append('"%s"' % u.id)
                    lines.append(" ".join(line))
                    continue
                except Exception:
                    warnings.warn("Can't find user for email %s" % email)

            line.append(field)
            for reg, value in exp:
                if isinstance(value, basestring):
                    line.append('"%s"' % value)
                elif isinstance(value, float):
                    line.append('"%s"' % time.strftime(
                        "%Y-%m-%d",
                        time.localtime(value)
                    ))
                else:
                    raise RuntimeError("Can't create line for %s" % exp)
            lines.append(" ".join(line))
        lines.append("allow any" if default_p else "deny all")
        new_firerole = "\n".join(lines)
        if firerole != new_firerole:
            updates.append((d.id, "firerole: %s" % new_firerole))

    for docid, status in updates:
        Bibdoc.query.filter_by(id=docid).update(dict(status=status))


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
