# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


from __future__ import absolute_import, print_function, unicode_literals

from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound

from invenio.ext.sqlalchemy import db

from .signals import resource_usage_updated


class Metric(object):

    """Metric."""

    metric_class = ""
    object_type = None

    @classmethod
    def get_id(cls, prop):
        """Get metric id."""
        return ".".join([cls.metric_class, prop])

    @classmethod
    def all(cls):
        """Compute metrics for all resources."""
        raise NotImplementedError()


class ResourceUsage(db.Model):

    """Usage of a specific.

    Note: Model is not suitable to store metrics with high granularity.
    """

    __tablename__ = 'quotaUSAGE'

    __table_args__ = (
        # Requires object_type, object_id and metric combined to be less than
        # ~333 chars due to MyISAM constraint.
        db.UniqueConstraint('object_type', 'object_id', 'metric'),
        db.Model.__table_args__
    )

    id = db.Column(db.Integer(15, unsigned=True), nullable=False,
                   primary_key=True, autoincrement=True)

    object_type = db.Column(db.String(40), index=True)
    """Generic relationship to an object type."""

    object_id = db.Column(db.String(250), index=True)
    """Generic relationship to an object."""

    metric = db.Column(db.String(40))
    """Metric."""

    value = db.Column(db.Integer(15, unsigned=True), nullable=False, default=0)

    modified = db.Column(db.DateTime, nullable=False, default=datetime.now,
                         onupdate=datetime.now)
    """Modification timestamp."""

    @classmethod
    def create(cls, object_type, object_id, metric, value):
        """Update or create a new value of a metric."""
        m = cls(object_type=object_type, object_id=object_id, metric=metric,
                value=value)
        db.session.add(m)
        db.session.commit()
        return m

    @classmethod
    def update_or_create(cls, object_type, object_id, metric, value):
        """Update or create a new value of a metric."""
        m = cls.get(object_type, object_id, metric)

        if m is None:
            m = cls.create(object_type, object_id, metric, value)

            resource_usage_updated.send(
                metric,
                object_type=object_type,
                object_id=object_id,
                value=value,
                old_value=None
            )
        else:
            old_value = m.value
            m.value = value
            db.session.commit()

            resource_usage_updated.send(
                metric,
                object_type=object_type,
                object_id=object_id,
                value=value,
                old_value=old_value
            )
        return m

    @classmethod
    def get(cls, object_type, object_id, metric):
        """Get specific metric."""
        try:
            return cls.query.filter_by(
                object_type=object_type,
                object_id=object_id,
                metric=metric
            ).one()
        except NoResultFound:
            return None
