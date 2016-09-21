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

"""CLI for Zenodo-specific tasks."""

from __future__ import absolute_import, print_function

import click
from flask_cli import with_appcontext
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record

from zenodo.modules.deposit.tasks import datacite_register


@click.group()
def utils():
    """Zenodo helper CLI."""

@utils.command('datacite_register')
@click.argument('recid', type=str)
@click.option('--eager', '-e', is_flag=True)
@with_appcontext
def datecite_register(recid, eager):
    """Send a record to DataCite for registration."""
    pid, record = Resolver(
        pid_type='recid', object_type='rec',
        getter=Record.get_record).resolve(recid)
    if eager:
        datacite_register.s(pid.pid_value, str(record.id)).apply(throw=True)
    else:
        datacite_register.s(pid.pid_value, str(record.id)).apply_async()
