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


"""Unit tests BibTex formatter."""

import datetime

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase
from invenio.base.wrappers import lazy_import
from invenio.base.globals import cfg
from zenodo.base.utils.bibtex import Bibtex, \
    MissingRequiredFieldError

Record = lazy_import('invenio.modules.records.models.Record')
get_record = lazy_import('invenio.modules.records.api.get_record')

test_record = dict(
    recid=1,
    system_number={"system_number": 2, "recid": 3},
    system_control_number={
        "system_control_number": "4", "institute": "CERN"},
    doi="10.1234/foo.bar",
    oai={"oai": "oai:zenodo.org:1",
         "indicator": ["user-zenodo", "user-ecfunded"]},
    upload_type={'type': 'publication', 'subtype': 'book'},
    collections=[{'primary': "pri", "secondary": "secondary", }],
    publication_date=datetime.date(2014, 2, 27),
    title="Test title",
    authors=[
        {'name': 'Doe, John', 'affiliation': 'CERN'},
        {'name': 'Smith, John', 'affiliation': 'CERN'},
    ],
    _first_author={
        "familyname": "Test"
    },
    _id="12345",
    description="Test Description",
    keywords=["kw1", "kw2", "kw3"],
    notes="notes",
    access_right="open",
    embargo_date="2014-02-27",
    license={'identifier': 'cc-by', 'url': 'http://zenodo.org',
             'source': 'opendefinition.org',
             'license': 'Creative Commons', },
    imprint={
        'place': "Staszkowka",
        'publisher': "Jol"
    },
    communities=["zenodo"],
    provisional_communities=["ecfunded"],
    grants=[
        {"title": "Grant Title", "identifier": "1234", },
        {"title": "Title Grant", "identifier": "4321", },
    ],
    # Test all schemes
    related_identifiers=[
        {"identifier": "10.1234/foo.bar",
            "scheme": "doi", "relation": "cites"},
        {"identifier": "1234.4321", "scheme":
            "arxiv", "relation": "cites"},
    ],
    meetings={
        'title': 'The 13th Biennial HITRAN Conference',
        'place': 'Harvard-Smithsonian Center for Astrophysics',
        'dates': '23-25 June, 2014',
        'acronym': 'HITRAN13',
        'session': 'VI',
        'session_part': '1',
    },
    altmetric_id="9876",
    preservation_score="100",
    references=[
        {'raw_reference': 'Doe, John et al (2012). Some title. ZENODO. '
                          '10.5281/zenodo.12'},
        {'raw_reference': 'Smith, Jane et al (2012). Some title. ZENODO. '
                          '10.5281/zenodo.34'},
    ],
    part_of={
        'title': 'Bum'
    },
    journal={
        'title': 'Bam',
        'issue': 2,
        'pages': 20,
        'volume': 20
    },
    thesis_university='I guess improtant',
    url=[
        {'url': 'one'},
        {'url': 'two'}
    ]
)

test_bad_record = dict(
    _id="12345",
    _first_author={
        "familyname": "Test Test"
    },
)


class BibTexFormatterTest(InvenioTestCase):

    def setUp(self):
        records = []
        record_list = Record.query.all()
        for rec in record_list:
            rec = get_record(rec.id)
            if rec:
                records.append(rec)
        self.dbrecords = records
        self.record_good = Bibtex(test_record)
        self.record_bad = Bibtex(test_bad_record)
        self.record_empty = Bibtex({})

    def test_get_entry_type(self):
        try:
            for r in self.dbrecords:
                b = Bibtex(r)
                self.assertEqual(r['upload_type']['type'],
                                 b._get_entry_type())
        except TypeError:
            import ipdb
            ipdb.set_trace()
        self.assertEqual(test_record['upload_type']['type'],
                         self.record_good._get_entry_type())
        self.assertEqual('default', self.record_bad._get_entry_type())

    def test_get_entry_subtype(self):
        self.assertEqual(test_record['upload_type']['subtype'],
                         self.record_good._get_entry_subtype())
        self.assertEqual('default',
                         self.record_bad._get_entry_subtype())

    def test_get_citation_key(self):
        good_id = test_record['_first_author']['familyname'] +\
            ":" + test_record['_id']

        self.assertEqual(good_id, self.record_good._get_citation_key())
        self.assertEqual(test_bad_record['_id'],
                         self.record_bad._get_citation_key())
        self.assertRaises(MissingRequiredFieldError,
                          self.record_empty._get_citation_key)

    def test_get_doi(self):
        self.assertEqual(test_record['doi'],
                         self.record_good._get_doi())
        self.assertRaises(MissingRequiredFieldError,
                          self.record_empty._get_doi)

    def test_get_author(self):
        authors = []
        for author in test_record['authors']:
            authors.append(author['name'])

        self.assertEqual(authors, self.record_good._get_author())
        self.assertEqual([], self.record_empty._get_author())

    def test_get_title(self):
        self.assertEqual(test_record['title'],
                         self.record_good._get_title())
        self.assertEqual("", self.record_empty._get_title())

    def test_get_month(self):
        good_month = test_record['publication_date'].strftime("%B")[:3].lower()

        self.assertEqual(good_month, self.record_good._get_month())
        self.assertEqual("", self.record_empty._get_month())

    def test_get_year(self):
        self.assertEqual(test_record['publication_date'].strftime("%Y"),
                         self.record_good._get_year())
        self.assertEqual("", self.record_empty._get_year())

    def test_get_note(self):
        self.assertEqual(test_record['notes'],
                         self.record_good._get_note())
        self.assertEqual("", self.record_empty._get_note())

    def test_get_address(self):
        self.assertEqual(test_record["imprint"]["place"],
                         self.record_good._get_address())
        self.assertEqual("", self.record_empty._get_note())

    def test_get_annote(self):
        self.assertEqual("", self.record_good._get_annote())
        self.assertEqual("", self.record_empty._get_annote())

    def test_get_booktitle(self):
        self.assertEqual(test_record["part_of"]["title"],
                         self.record_good._get_booktitle())
        self.assertEqual("", self.record_empty._get_booktitle())

    def test_get_chapter(self):
        self.assertEqual("", self.record_good._get_chapter())
        self.assertEqual("", self.record_empty._get_chapter())

    def test_get_edition(self):
        self.assertEqual("", self.record_good._get_edition())
        self.assertEqual("", self.record_empty._get_edition())

    def test_get_editor(self):
        self.assertEqual("", self.record_good._get_editor())
        self.assertEqual("", self.record_empty._get_editor())

    def test_get_crossref(self):
        self.assertEqual("", self.record_good._get_crossref())
        self.assertEqual("", self.record_empty._get_crossref())

    def test_get_howpublished(self):
        self.assertEqual("", self.record_good._get_howpublished())
        self.assertEqual("", self.record_empty._get_howpublished())

    def test_get_institution(self):
        self.assertEqual("", self.record_good._get_institution())
        self.assertEqual("", self.record_empty._get_institution())

    def test_get_journal(self):
        self.assertEqual(test_record['journal']['title'],
                         self.record_good._get_journal())
        self.assertEqual("", self.record_empty._get_journal())

    def test_get_key(self):
        self.assertEqual("", self.record_good._get_key())
        self.assertEqual("", self.record_empty._get_key())

    def test_get_number(self):
        self.assertEqual(test_record['journal']['issue'],
                         self.record_good._get_number())
        self.assertEqual("", self.record_empty._get_number())

    def test_get_organization(self):
        self.assertEqual("", self.record_good._get_organization())
        self.assertEqual("", self.record_empty._get_organization())

    def test_get_pages(self):
        self.assertEqual(test_record['journal']['pages'],
                         self.record_good._get_pages())
        self.assertEqual("", self.record_empty._get_pages())

    def test_get_publisher(self):
        global_cfg = ""
        if "CFG_SITE_NAME" in cfg:
            global_cfg = cfg["CFG_SITE_NAME"]
        self.assertEqual(test_record['imprint']['publisher'],
                         self.record_good._get_publisher())
        self.assertEqual(global_cfg,
                         self.record_empty._get_publisher())

    def test_get_school(self):
        self.assertEqual(test_record['thesis_university'],
                         self.record_good._get_school())
        self.assertEqual("", self.record_empty._get_school())

    def test_get_series(self):
        self.assertEqual("", self.record_good._get_series())
        self.assertEqual("", self.record_empty._get_series())

    def test_get_type(self):
        self.assertEqual("", self.record_good._get_type())
        self.assertEqual("", self.record_empty._get_type())

    def test_get_url(self):
        url = "http://dx.doi.org/" + test_record['doi']
        self.assertEqual(url, self.record_good._get_url())
        self.assertEqual("", self.record_empty._get_url())

    def test_get_volume(self):
        self.assertEqual(test_record['journal']['volume'],
                         self.record_good._get_volume())
        self.assertEqual("", self.record_empty._get_volume())

TEST_SUITE = make_test_suite(BibTexFormatterTest)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE)
