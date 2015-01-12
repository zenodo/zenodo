# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2014 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

""" Database models for extra indices definded in Zenodo. """

from invenio.ext.sqlalchemy import db
from invenio.modules.records.models import Record as Bibrec


class IdxPHRASE29F(db.Model):

    """Represents a IdxPHRASE29F record."""

    __tablename__ = 'idxPHRASE29F'

    id = db.Column(db.MediumInteger(9, unsigned=True),
                   primary_key=True,
                   autoincrement=True)
    term = db.Column(db.Text, nullable=True)
    hitlist = db.Column(db.iLargeBinary, nullable=True)


class IdxPHRASE29R(db.Model):

    """Represents a IdxPHRASE29R record."""

    __tablename__ = 'idxPHRASE29R'

    id_bibrec = db.Column(db.MediumInteger(8, unsigned=True),
                          db.ForeignKey(Bibrec.id),
                          primary_key=True)
    termlist = db.Column(db.iLargeBinary, nullable=True)
    type = db.Column(db.Enum('CURRENT', 'FUTURE', 'TEMPORARY'),
                     nullable=False,
                     server_default='CURRENT',
                     primary_key=True)


class IdxWORD29F(db.Model):

    """Represents a IdxWORD29F record."""

    __tablename__ = 'idxWORD29F'

    id = db.Column(db.MediumInteger(9, unsigned=True),
                   primary_key=True,
                   autoincrement=True)
    term = db.Column(db.String(50), nullable=True,
                     unique=True)
    hitlist = db.Column(db.iLargeBinary, nullable=True)


class IdxWORD29R(db.Model):

    """Represents a IdxWORD29R record."""

    __tablename__ = 'idxWORD29R'

    id_bibrec = db.Column(db.MediumInteger(8, unsigned=True),
                          db.ForeignKey(Bibrec.id),
                          primary_key=True)
    termlist = db.Column(db.iLargeBinary, nullable=True)
    type = db.Column(db.Enum('CURRENT', 'FUTURE', 'TEMPORARY'),
                     nullable=False,
                     server_default='CURRENT',
                     primary_key=True)


class IdxPAIR29F(db.Model):

    """Represents a IdxPAIR29F record."""

    __tablename__ = 'idxPAIR29F'

    id = db.Column(db.MediumInteger(9, unsigned=True),
                   primary_key=True,
                   autoincrement=True)
    term = db.Column(db.String(100), nullable=True,
                     unique=True)
    hitlist = db.Column(db.iLargeBinary, nullable=True)


class IdxPAIR29R(db.Model):

    """Represents a IdxPAIR28R record."""

    __tablename__ = 'idxPAIR29R'

    id_bibrec = db.Column(db.MediumInteger(8, unsigned=True),
                          db.ForeignKey(Bibrec.id),
                          primary_key=True)
    termlist = db.Column(db.iLargeBinary, nullable=True)
    type = db.Column(db.Enum('CURRENT', 'FUTURE', 'TEMPORARY'),
                     nullable=False,
                     server_default='CURRENT',
                     primary_key=True)
