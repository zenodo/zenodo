# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
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

"""Database models for Zenodo Profiles."""

from __future__ import absolute_import, print_function

from invenio_accounts.models import User
from invenio_db import db
from sqlalchemy import event, ForeignKeyConstraint, PrimaryKeyConstraint


class Profile(db.Model):
    """Profile model.

    Profile store additional information about account users.
    """

    __tablename__ = 'zenodo_profiles_profiles'

    user_id = db.Column(db.Integer)
    """Foreign key to user."""

    researcher_profile = db.relationship(
        User, backref=db.backref(
            'researcher_profile', uselist=False, cascade='all, delete-orphan')
    )
    """User relationship."""

    bio = db.Column(db.String(255))
    """Bio of user."""

    affiliation = db.Column(db.String(255))
    """Affiliation(University/Institute) of user."""

    location = db.Column(db.String(255))
    """Location of user."""

    website = db.Column(db.String(255))
    """Website or external link of user."""

    show_profile = db.Column(db.Boolean(name='show_profile'))
    """Permission field to show profile."""

    allow_contact_owner = db.Column(db.Boolean(name='allow_contact_owner'))
    """Permission field to allow other user to contact the user."""

    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='pk_zenodo_profiles_profiles'),
        ForeignKeyConstraint(['user_id'], ['accounts_user.id'],
                             name='fk_zenodo_profiles_profiles_user_id'),
    )

    @classmethod
    def get_by_userid(cls, user_id):
        """Get profile by user identifier.

        :param user_id: The :class:`invenio_accounts.models.User` ID.
        :returns: A :class:`zenodo_profiles.models.Profile` instance
            or ``None``.
        """
        return cls.query.filter_by(user_id=user_id).one_or_none()


@event.listens_for(User, 'init')
def on_user_init(target, args, kwargs):
    """Provide hook on User initialization."""
    researcher_profile = Profile()
    if kwargs.get('id'):
        researcher_profile.user_id = kwargs['id']
    kwargs['researcher_profile'] = researcher_profile
