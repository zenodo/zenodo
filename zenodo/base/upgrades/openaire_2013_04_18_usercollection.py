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

depends_on = ['openaire_2013_03_20_datacite_output_fmt']


def info():
    return "Create userCOLLECTION"


def do_upgrade():
    """ Implement your upgrades here  """
    m = db.MetaData(bind=db.engine)
    m.reflect()
    t = db.Table(
        'userCOLLECTION',
        m,
        db.Column('id', db.String(length=100), primary_key=True, nullable=False),
        db.Column('id_user', db.Integer(15, unsigned=True), db.ForeignKey('user.id'), nullable=False),
        db.Column('id_collection', db.MediumInteger(9, unsigned=True), db.ForeignKey('collection.id'), nullable=True),
        db.Column('id_collection_provisional', db.MediumInteger(9, unsigned=True), db.ForeignKey('collection.id'), nullable=True),
        db.Column('id_oairepository', db.MediumInteger(9, unsigned=True), db.ForeignKey('oaiREPOSITORY.id'), nullable=True),
        db.Column('title', db.String(length=255), nullable=False),
        db.Column('description', db.Text(), nullable=False),
        db.Column('page', db.Text(), nullable=False),
        db.Column('curation_policy', db.Text(), nullable=False),
        db.Column('has_logo', db.Boolean(), nullable=False),
        db.Column('created', db.DateTime(), nullable=False),
        db.Column('last_modified', db.DateTime(), nullable=False),
        mysql_engine='MyISAM',
    )
    t.create()
