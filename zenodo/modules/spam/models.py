# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2022 CERN.
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

"""Spam models."""

from datetime import datetime

from invenio_accounts.models import User
from invenio_db import db
from sqlalchemy.dialects import mysql


class SafelistEntry(db.Model):
    """Defines an entry in the safelist."""

    __tablename__ = "safelist_entries"
    __versioned__ = {"versioning": False}

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(User.id, ondelete='RESTRICT'),
        primary_key=True,
        nullable=False
    )
    """The safelisted user."""

    notes = db.Column(
        db.Text,
        nullable=True
    )
    """Notes about the safelisting."""

    created = db.Column(
        db.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
        default=datetime.utcnow,
        nullable=False,
    )

    user = db.relationship(User, backref='safelist')

    @classmethod
    def create(cls, user_id, notes=None):
        """Create a safelist entry."""
        try:
            entry = cls(user_id=user_id, notes=notes)
            db.session.add(entry)
        except Exception:
            entry = None

        return entry

    @classmethod
    def get_by_user_id(cls, user_id):
        """Get entry by user_id."""
        try:
            entry = cls.query.filter(cls.user_id == user_id).first()
        except Exception:
            entry = None

        return entry

    @classmethod
    def remove_by_user_id(cls, user_id):
        """Delete entry by user_id."""
        try:
            entry = cls.query.filter(cls.user_id == user_id).first()
            db.session.delete(entry)
        except Exception:
            pass

    @classmethod
    def get_record_status(cls, record):
        """Get entry by user_id."""
        for owner_id in record.get("owners", []):
            if cls.get_by_user_id(owner_id):
                return True
        return False
