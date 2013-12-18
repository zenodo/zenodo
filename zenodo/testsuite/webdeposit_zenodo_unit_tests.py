# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2012, 2013 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from invenio.testutils import make_test_suite, run_test_suite, \
    InvenioTestCase
from invenio.bibfield import get_record
from invenio.bibfield_jsonreader import JsonReader
import datetime

test_data = {'access_right': u'embargoed',
 'authors': [{'affiliation': 'Atlantis', 'name': 'Doe, John'},
  {'affiliation': 'Atlantis', 'name': 'Smith, Jane'}],
 'conference_url': 'http://someurl.com',
 'description': '<p>Test <em>Description</em></p>',
 'doi': '10.5072/zenodo.7873',
 'embargo_date': datetime.date(2010, 12, 9),
 'fft': [{'name': 'test',
   'path': u'/home/lnielsen/envs/zenodomaster/var/data/deposit/storage/2303/6611c9a4-2b10-44b4-9d01-4ba69108d5c7-test.pdf'}],
 'grants': [{'acronym': u'OPENAIREPLUS',
   'id': '283595',
   'title': u'2nd-Generation Open Access Infrastructure for Research in Europe'}],
 'imprint.place': 'Some place',
 'imprint.publisher': 'Some publisher',
 'isbn': 'Some isbn',
 'journal.issue': 'Some issue',
 'journal.pages': 'Some pages',
 'journal.title': 'Some journal name',
 'journal.volume': 'Some volume',
 'keywords': ['Keyword 1', 'keyword 2'],
 'license': u'cc-by',
 'meetings.acronym': 'Some acronym',
 'meetings.dates': 'Some dates',
 'meetings.place': 'Some place',
 'meetings.title': 'Some title',
 'notes': 'Some notes',
 #'part_of.pages': 'SOme part of',
 #'part_of.title': 'Some part of title',
 'provisional_communities': [{'identifier': 'cfa',
   'provisional': True,
   'title': u'Harvard-Smithsonian Center for Astrophysics'}],
 'publication_date': datetime.date(2013, 5, 8),
 'recid': '7873',
 'related_identifiers': [{'identifier': '10.1234/foo.bar2',
   'relation': u'isCitedBy',
   'scheme': 'doi'},
   {'identifier': '10.1234/foo.bar3', 'relation': u'cites', 'scheme': 'doi'}],
 'thesis_supervisors': [{'affiliation': 'Atlantis', 'name': 'Doe Sr., John'},
                        {'affiliation': 'Atlantis', 'name': 'Smith Sr., Jane'}],
 'thesis_university': 'Some thesis_university',
 'title': u'My new title',
 'upload_type.subtype': u'book',
 'upload_type.type': u'publication',
 'version_id': datetime.datetime(2013, 11, 28, 10, 38, 12)}


class WebDepositZenodoTest(InvenioTestCase):
    #
    # Tests
    #
    def test_recorddiff(self):
        record = JsonReader()

        for k, v in test_data.items():
            record[k] = v

        from pprint import pprint
        pprint(record.rec_json)


TEST_SUITE = make_test_suite(WebDepositZenodoTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
