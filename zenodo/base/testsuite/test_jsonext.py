# -*- coding: utf-8 -*-
##
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
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


""" Unit tests jsonext """

from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase
from datetime import date


test_marc = """<record><datafield tag="942" ind1="" ind2=""><subfield code="a">2014-02-27</subfield></datafield>
<datafield tag="520" ind1="" ind2=""><subfield code="a">Test Description</subfield></datafield>
<datafield tag="100" ind1="" ind2=""><subfield code="u">CERN</subfield><subfield code="a">Doe, John</subfield></datafield>
<datafield tag="980" ind1="" ind2=""><subfield code="a">provisional-user-ecfunded</subfield></datafield>
<datafield tag="035" ind1="" ind2=""><subfield code="a">4</subfield><subfield code="9">CERN</subfield></datafield>
<datafield tag="980" ind1="" ind2=""><subfield code="a">user-zenodo</subfield></datafield>
<datafield tag="536" ind1="" ind2=""><subfield code="c">1234</subfield><subfield code="a">Grant Title</subfield></datafield>
<datafield tag="536" ind1="" ind2=""><subfield code="c">4321</subfield><subfield code="a">Title Grant</subfield></datafield>
<datafield tag="980" ind1="" ind2=""><subfield code="b">book</subfield><subfield code="a">publication</subfield></datafield>
<datafield tag="653" ind1="1" ind2=""><subfield code="a">kw1</subfield></datafield>
<datafield tag="653" ind1="1" ind2=""><subfield code="a">kw2</subfield></datafield>
<datafield tag="653" ind1="1" ind2=""><subfield code="a">kw3</subfield></datafield>
<datafield tag="260" ind1="" ind2=""><subfield code="c">2014-02-27</subfield></datafield>
<datafield tag="035" ind1="" ind2=""><subfield code="9">Altmetric</subfield><subfield code="a">9876</subfield></datafield>
<datafield tag="970" ind1="" ind2=""><subfield code="d">3</subfield><subfield code="a">2</subfield></datafield>
<datafield tag="024" ind1="7" ind2=""><subfield code="2">DOI</subfield><subfield code="a">10.1234/foo.bar</subfield></datafield>
<datafield tag="540" ind1="" ind2=""><subfield code="u">http://zenodo.org</subfield><subfield code="a">Creative Commons</subfield></datafield>
<datafield tag="650" ind1="1" ind2="7"><subfield code="a">cc-by</subfield><subfield code="2">opendefinition.org</subfield></datafield>
<datafield tag="245" ind1="" ind2=""><subfield code="a">Test title</subfield></datafield>
<datafield tag="500" ind1="" ind2=""><subfield code="a">notes</subfield></datafield>
<datafield tag="909" ind1="C" ind2="O"><subfield code="o">oai:zenodo.org:1</subfield><subfield code="p">user-zenodo</subfield><subfield code="p">user-ecfunded</subfield></datafield>
<datafield tag="700" ind1="" ind2=""><subfield code="u">CERN</subfield><subfield code="a">Doe, Jane</subfield></datafield>
<datafield tag="700" ind1="" ind2=""><subfield code="u">CERN</subfield><subfield code="a">Smith, John</subfield></datafield>
<datafield tag="980" ind1="" ind2=""><subfield code="b">secondary</subfield><subfield code="a">pri</subfield></datafield>
<controlfield tag="001">1</controlfield>
<datafield tag="542" ind1="" ind2=""><subfield code="l">open</subfield></datafield>
<datafield tag="773" ind1="" ind2=""><subfield code="a">10.1234/foo.bar</subfield><subfield code="i">cites</subfield><subfield code="n">doi</subfield></datafield>
<datafield tag="773" ind1="" ind2=""><subfield code="a">1234.4321</subfield><subfield code="i">cites</subfield><subfield code="n">arxiv</subfield></datafield>
</record>"""

test_form_json = {
    'access_right': 'open',
    'communities': [
        {'identifier': 'ecfunded', 'provisional': True},
        {'identifier': 'zenodo', 'provisional': False}],
    'creators': [
        {'affiliation': 'CERN', 'name': 'Doe, John'},
        {'affiliation': 'CERN', 'name': 'Doe, Jane'},
        {'affiliation': 'CERN', 'name': 'Smith, John'}
    ],
    'description': 'Test Description',
    'doi': '10.1234/foo.bar',
    'embargo_date': date(2014, 2, 27),
    'grants': [{'id': '1234'}, {'id': '4321'}],
    'image_type': '',
    'keywords': ['kw1', 'kw2', 'kw3'],
    'license': 'cc-by',
    'notes': 'notes',
    'publication_date': date(2014, 2, 27),
    'publication_type': 'book',
    'recid': 1,
    'related_identifiers': [
        {'identifier': '10.1234/foo.bar',
         'relation': 'cites',
         'scheme': 'doi'},
        {'identifier': '1234.4321', 'relation': 'cites', 'scheme': 'arxiv'}],
    'title': 'Test title',
    'upload_type': 'publication'
}

test_record = dict(
    recid=1,
    system_number={"system_number": 2, "recid": 3},
    system_control_number={
        "system_control_number": "4", "institute": "CERN"},
    doi="10.1234/foo.bar",
    # Test with and without several indicators
    oai={"oai": "oai:zenodo.org:1",
         "indicator": ["user-zenodo", "user-ecfunded"]},
    upload_type={'type': 'publication', 'subtype': 'book'},
    collections=[{'primary': "pri", "secondary": "secondary", }],
    publication_date="2014-02-27",
    title="Test title",
    authors=[
        {'name': 'Doe, John', 'affiliation': 'CERN'},
        {'name': 'Doe, Jane', 'affiliation': 'CERN'},
        {'name': 'Smith, John', 'affiliation': 'CERN'},
    ],
    description="Test Description",
    keywords=["kw1", "kw2", "kw3"],
    notes="notes",
    access_right="open",
    embargo_date="2014-02-27",
    license={'identifier': 'cc-by', 'url': 'http://zenodo.org',
             'source': 'opendefinition.org',
             'license': 'Creative Commons', },

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
    altmetric_id="9876",
)


class TestReaders(InvenioTestCase):

    def test_json_for_form(self):
        from invenio.modules.records.api import Record
        r = Record.create({'title': 'Test'}, 'json')
        assert r.produce('json_for_form')['title'] == 'Test'
        assert {'245__a': 'Test'} in r.produce('json_for_marc')

        import copy
        r = Record(json=copy.copy(test_record), master_format='marc')

        form_json = r.produce('json_for_form')
        for k, v in test_form_json.items():
            self.assertEqual(form_json[k], test_form_json[k])

    def test_marc_export(self):
        from invenio.modules.records.api import Record
        from invenio.legacy.bibrecord import create_record

        r = Record(json=test_record, master_format='marc')
        self.assertEqual(
            r.legacy_create_recstruct(),
            create_record(test_marc)[0],
        )

        form_json = r.produce('json_for_form')
        for k, v in test_form_json.items():
            self.assertEqual(form_json[k], test_form_json[k])

    def test_lossless_marc_import_export(self):
        from invenio.modules.records.api import Record
        r = Record.create(test_marc, master_format='marc').dumps()

        for k in test_record.keys():
            self.assertEqual(test_record[k], r[k])


TEST_SUITE = make_test_suite(TestReaders)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE)
