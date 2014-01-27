# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from sqlalchemy import *
from invenio.ext.sqlalchemy import db

depends_on = ['openaire_2013_04_18_usercollection']


def info():
    return "Create pid, pidLOG, pidREGISTRY"


def do_upgrade():
    """ Implement your upgrades here  """
    m = db.MetaData(bind=db.engine)
    m.reflect()

    tpid = db.Table(
        'pid',
        m,
        db.Column('id', db.Integer(15, unsigned=True), primary_key=True, nullable=False),
        db.Column('type', db.String(length=6), nullable=False),
        db.Column('pid', db.String(length=255), nullable=False),
        db.Column('status', db.Char(length=1), nullable=False),
        db.Column('created', db.DateTime(), nullable=False),
        db.Column('last_modified', db.DateTime(), nullable=False),
        db.Index('uidx_type_pid', 'type', 'pid', unique=True),
        db.Index('idx_status', 'status'),
        mysql_engine='MyISAM',
    )

    tpidlog = db.Table(
        'pidLOG',
        m,
        db.Column('id', db.Integer(15, unsigned=True), primary_key=True, nullable=False),
        db.Column('id_pid', db.Integer(15, unsigned=True), ForeignKey('pid.id')),
        db.Column('timestamp', DateTime(), nullable=False),
        db.Column('action', db.String(length=10), nullable=False),
        db.Column('message', Text(), nullable=False),
        db.Index('idx_action', 'action'),
        mysql_engine='MyISAM',
    )

    tpidregistry = db.Table(
        'pidREGISTRY',
        m,
        db.Column('object_type', db.String(length=3), primary_key=True, nullable=False),
        db.Column('object_id', db.String(length=255), nullable=False),
        db.Column('id_pid', db.Integer(15, unsigned=True), ForeignKey('pid.id'), primary_key=True, nullable=False),
        db.Index('idx_type_id', 'object_type', 'object_id'),
        mysql_engine='MyISAM',
    )

    tpid.create()
    tpidlog.create()
    tpidregistry.create()
