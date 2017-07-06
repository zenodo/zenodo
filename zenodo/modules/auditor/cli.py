# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""CLI for Zenodo-Auditor tasks."""

from __future__ import absolute_import, print_function

import click
from flask.cli import with_appcontext

from .tasks import audit_oai, audit_records


@click.group()
def audit():
    """Zenodo Auditor CLI."""


@audit.command('records')
@click.option('--logfile', '-l', type=click.Path(exists=False, dir_okay=False,
                                                 resolve_path=True))
@click.option('--eager', '-e', is_flag=True)
@with_appcontext
def _audit_records(logfile, eager):
    """Audit all records."""
    if eager:
        audit_records.apply((logfile,), throw=True)
    else:
        audit_records.apply_async((logfile,))


@audit.command('oai')
@click.option('--logfile', '-l', type=click.Path(exists=False, dir_okay=False,
                                                 resolve_path=True))
@click.option('--eager', '-e', is_flag=True)
@with_appcontext
def _audit_oai(logfile, eager):
    """Audit OAI Sets."""
    if eager:
        audit_oai.apply((logfile,), throw=True)
    else:
        audit_oai.apply_async((logfile,))
