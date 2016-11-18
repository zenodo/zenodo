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

"""Zenodo Auditor API."""

import json

from .utils import tree


class Audit(object):
    """Audit base class."""

    def __init__(self, audit_id, logger):
        """Initialize an Audit with a logger."""
        self.audit_id = audit_id
        self.logger = logger
        self._checks = None

    def __iter__(self):
        """Get iterator."""
        return self

    def next(self):
        """Python 2.7 compatibility."""
        return self.__next__()

    def __next__(self):
        """Get, perform and log the next check."""
        check = next(self._checks)
        try:
            check.perform()
        except Exception:
            self.logger.exception(json.dumps(check.dump()))
        finally:
            if not check.is_ok:
                print(json.dumps(check.dump()))
                self.logger.error(json.dumps(check.dump()))
        return check


class Check(object):
    """Audit Check base class."""

    def __init__(self):
        """Initialize a Check."""
        self.issues = tree()

    def perform(self, **kwargs):
        """Perform the check."""
        raise NotImplementedError()

    def dump(self):
        """Dump check issues."""
        return {'issues': self.issues}

    @property
    def is_ok(self):
        """Get if check is considered passed."""
        return not bool(self.issues)
