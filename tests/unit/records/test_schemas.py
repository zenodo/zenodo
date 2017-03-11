# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
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

"""Zenodo template tests."""

from __future__ import absolute_import, print_function

from datetime import datetime

import pytest
from invenio_records.api import Record
from jsonschema.exceptions import ValidationError


def test_minimal_json(app, db, minimal_record):
    """Test minimal json."""
    Record.create(minimal_record)


def test_recid(app, db, minimal_record):
    """Test recid property."""
    # String instead of number
    minimal_record['recid'] = '123'
    pytest.raises(ValidationError, Record.create, minimal_record)


def test_resource_type(app, db, minimal_record):
    """Test resource type."""
    # String instead of number
    minimal_record['resource_type'] = 'publication'
    pytest.raises(ValidationError, Record.create, minimal_record)
    minimal_record['resource_type'] = {'type': 'publication', 'subtype': 'x'}
    Record.create(minimal_record)


def test_publication_date(app, db, minimal_record):
    """Test publication date."""
    # String instead of numbe
    minimal_record['publication_date'] = datetime.utcnow().date().isoformat()
    Record.create(minimal_record)

    
def test_contributors(app, db, minimal_record):
    """Test contributors."""
    # String instead of number
    minimal_record['contributors'] = [
        {'name': 'test', 'affiliation': 'test', 'type': 'ContactPerson'}
    ]
    Record.create(minimal_record)
    minimal_record['contributors'] = [
        {'name': 'test', 'affiliation': 'test', 'type': 'Invalid'}
    ]
    pytest.raises(ValidationError, Record.create, minimal_record)
     # validation of full_record fixture
    
def test_full_json(app, db, full_record) :
      """Test full json."""
    Record.create(full_record)
      
def full_test_recid(app,db,full_record):
    """Test recid property."""
    
    full_record['recid'] = '12345'
    pytest.raises(ValidationError, Record.create, full_record)
      
def full_test_resource_type(app, db, full_record):
    """Test resource type."""
    
    full_record['resource_type'] = 'publication'
    pytest.raises(ValidationError, Record.create, full_record)
    full_record['resource_type'] = {'type': 'publication', 'subtype': 'book'}
    Record.create(full_record) 
    
def full_test_contributors(app, db, full_record):
    """Test contributors."""
    
    full_record['contributors'] = [
       {'affiliation': 'CERN', 'name': 'Smith, Other', 'type': 'Other',
             'gnd': '', 'orcid': '0000-0002-1825-0097'}
    ]
    Record.create(full_record)
    full_record['contributors'] = [
        {'affiliation': '', 'name': 'Hansen, Viggo', 'type': 'Other',
             'gnd': '', 'orcid': ''} 
    ]
    pytest.raises(ValidationError, Record.create, full_record)          
    
    
    
      
     

