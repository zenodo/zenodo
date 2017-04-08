# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
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

import pytest
from invenio_records.api import Record
from invenio_records.models import RecordMetadata

from zenodo.modules.records.serializers.bibtex import Bibtex, \
    BibTeXSerializer, MissingRequiredFieldError


def test_serializer(bibtex_records):
    """Test serializer."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    serializer = BibTeXSerializer()
    bibtex = ("""@book{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title},\n"""
              """  publisher    = {Jol},\n"""
              """  year         = 2014,\n"""
              """  volume       = 20,\n"""
              """  address      = {Staszkowka},\n"""
              """  month        = feb,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == serializer.serialize(record=test_record, pid=1)
    results = {
        "hits": {
            "hits": [{
                "_source": test_record
            }]
        }
    }
    assert bibtex == serializer.serialize_search(search_result=results,
                                                 pid_fetcher=None)


def test_get_entry_type(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records

    for rec, in RecordMetadata.query.values(RecordMetadata.id):
        if rec != record_bad.record.id:
            r = Record.get_record(id_=rec)
            b = Bibtex(r)
            assert r['resource_type']['type'] == b._get_entry_type()

    assert test_record['resource_type']['type'] == \
        record_good._get_entry_type()
    assert 'default' == record_bad._get_entry_type()


def test_get_entry_subtype(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    assert test_record['resource_type']['subtype'] == \
        record_good._get_entry_subtype()
    assert 'default' == record_bad._get_entry_subtype()


def test_get_citation_key(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    assert "doe_2014_12345" == record_good._get_citation_key()
    assert "12345" == record_bad._get_citation_key()
    with pytest.raises(MissingRequiredFieldError) as exc_info:
        record_empty._get_citation_key()
    assert exc_info.type is MissingRequiredFieldError


def test_get_doi(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    assert test_record['doi'] == record_good._get_doi()
    assert record_empty._get_doi() is None


def test_get_author(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    authors = []
    for author in test_record['creators']:
        authors.append(author['name'])

    assert authors == record_good._get_author()
    assert [] == record_empty._get_author()


def test_get_title(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    assert test_record['title'] == record_good._get_title()
    assert "" == record_empty._get_title()


def test_get_month(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records

    assert 'feb' == record_good._get_month()
    assert "" == record_empty._get_month()


def test_get_year(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    assert '2014' == record_good._get_year()
    assert "" == record_empty._get_year()


def test_get_note(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    assert test_record['notes'] == record_good._get_note()
    assert "" == record_empty._get_note()


def test_get_address(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    assert test_record["imprint"]["place"] == record_good._get_address()
    assert "" == record_empty._get_note()


def test_get_booktitle(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    assert test_record["part_of"]["title"] == record_good._get_booktitle()
    assert "" == record_empty._get_booktitle()


def test_get_journal(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    assert test_record['journal']['title'] == record_good._get_journal()
    assert "" == record_empty._get_journal()


def test_get_number(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    assert test_record['journal']['issue'] == record_good._get_number()
    assert "" == record_empty._get_number()


def test_get_pages(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    assert test_record['journal']['pages'] == record_good._get_pages()
    assert "" == record_empty._get_pages()


def test_get_publisher(app, bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    with app.app_context():
        global_cfg = app.config['THEME_SITENAME']
    assert test_record['imprint']['publisher'] == record_good._get_publisher()
    assert global_cfg == record_empty._get_publisher()


def test_get_school(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    assert test_record['thesis']['university'] == record_good._get_school()
    assert "" == record_empty._get_school()


def test_get_url(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    url = "https://doi.org/" + test_record['doi']
    assert url == record_good._get_url()
    assert "" == record_empty._get_url()


def test_get_volume(bibtex_records):
    """Test."""
    (record_good, record_bad, record_empty, test_record) = bibtex_records
    assert test_record['journal']['volume'] == record_good._get_volume()
    assert "" == record_empty._get_volume()


def test_clean_input(full_record):
    """Test."""
    full_record['resource_type']['subtype'] = 'article'
    full_record['title'] = "Test title & escaped character"
    bibtex = ("""@article{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title \& escaped character},\n"""
              """  journal      = {Bam},\n"""
              """  year         = 2014,\n"""
              """  volume       = 20,\n"""
              """  number       = 2,\n"""
              """  pages        = 20,\n"""
              """  month        = feb,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()


def test_format_article(full_record):
    """Test."""
    full_record['resource_type']['subtype'] = 'article'
    bibtex = ("""@article{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title},\n"""
              """  journal      = {Bam},\n"""
              """  year         = 2014,\n"""
              """  volume       = 20,\n"""
              """  number       = 2,\n"""
              """  pages        = 20,\n"""
              """  month        = feb,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()


def test_format_book(full_record):
    """Test."""
    full_record['resource_type']['subtype'] = 'book'
    bibtex = ("""@book{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title},\n"""
              """  publisher    = {Jol},\n"""
              """  year         = 2014,\n"""
              """  volume       = 20,\n"""
              """  address      = {Staszkowka},\n"""
              """  month        = feb,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()


def test_format_booklet(full_record):
    """Test."""
    full_record['resource_type']['subtype'] = 'book'
    del full_record['publication_date']
    bibtex = ("""@booklet{doe_12345,\n"""
              """  title        = {Test title},\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  address      = {Staszkowka},\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()


def test_format_inbook(full_record):
    """Test."""
    full_record['resource_type']['subtype'] = 'section'
    bibtex = ("""@misc{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title},\n"""
              """  month        = feb,\n"""
              """  year         = 2014,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()


def test_format_inproceedings(full_record):
    """Test."""
    full_record['resource_type']['subtype'] = 'conferencepaper'
    bibtex = ("""@inproceedings{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title},\n"""
              """  booktitle    = {Bum},\n"""
              """  year         = 2014,\n"""
              """  pages        = 20,\n"""
              """  publisher    = {Jol},\n"""
              """  address      = {Staszkowka},\n"""
              """  month        = feb,\n"""
              """  note         = {notes},\n"""
              """  venue        = """
              """{Harvard-Smithsonian Center for Astrophysics},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()

    del full_record['journal']
    full_record['part_of']['pages'] = "30"
    bibtex = ("""@inproceedings{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title},\n"""
              """  booktitle    = {Bum},\n"""
              """  year         = 2014,\n"""
              """  pages        = 30,\n"""
              """  publisher    = {Jol},\n"""
              """  address      = {Staszkowka},\n"""
              """  month        = feb,\n"""
              """  note         = {notes},\n"""
              """  venue        = """
              """{Harvard-Smithsonian Center for Astrophysics},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()

    del full_record['imprint']
    full_record['part_of']['publisher'] = "hello"
    bibtex = ("""@inproceedings{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title},\n"""
              """  booktitle    = {Bum},\n"""
              """  year         = 2014,\n"""
              """  pages        = 30,\n"""
              """  publisher    = {hello},\n"""
              """  month        = feb,\n"""
              """  note         = {notes},\n"""
              """  venue        = """
              """{Harvard-Smithsonian Center for Astrophysics},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()

    del full_record['meeting']
    bibtex = ("""@inproceedings{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title},\n"""
              """  booktitle    = {Bum},\n"""
              """  year         = 2014,\n"""
              """  pages        = 30,\n"""
              """  publisher    = {hello},\n"""
              """  month        = feb,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()


def test_format_proceedings(full_record):
    """Test."""
    full_record['resource_type']['subtype'] = 'conferencepaper'
    del full_record['part_of']
    bibtex = ("""@proceedings{doe_2014_12345,\n"""
              """  title        = {Test title},\n"""
              """  year         = 2014,\n"""
              """  publisher    = {Jol},\n"""
              """  address      = {Staszkowka},\n"""
              """  month        = feb,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()


def test_format_manual(full_record):
    """Test."""
    full_record['resource_type']['subtype'] = 'technicalnote'
    bibtex = ("""@manual{doe_2014_12345,\n"""
              """  title        = {Test title},\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  address      = {Staszkowka},\n"""
              """  month        = feb,\n"""
              """  year         = 2014,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()

    full_record['creators'].append({'name': 'Bar, Fuu', 'affiliation': 'CERN',
                                    'orcid': '', 'familyname': 'Bar',
                                    'givennames': 'Fuu'})
    bibtex = ("""@manual{doe_2014_12345,\n"""
              """  title        = {Test title},\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack and\n"""
              """                  Bar, Fuu},\n"""
              """  address      = {Staszkowka},\n"""
              """  month        = feb,\n"""
              """  year         = 2014,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()

    authors = ""
    for i in range(0, 50):
        full_record['creators'].append({
            'name': 'Bar, Fuu{0}'.format(i), 'affiliation': 'CERN',
            'orcid': '', 'familyname': 'Bar',
            'givennames': 'Fuu{0}'.format(i)})
        authors += "                  Bar, Fuu{0}".format(i)
        if i != 49:
            authors += " and\n"

    bibtex = ("@manual{doe_2014_12345,\n"
              "  title        = {Test title},\n"
              "  author       = {Doe, John and\n"
              "                  Doe, Jane and\n"
              "                  Smith, John and\n"
              "                  Nowak, Jack and\n"
              "                  Bar, Fuu and\n" +
              authors + "},\n"
              "  address      = {Staszkowka},\n"
              "  month        = feb,\n"
              "  year         = 2014,\n"
              "  note         = {notes},\n"
              "  doi          = {10.1234/foo.bar},\n"
              "  url          = {https://doi.org/10.1234/foo.bar}\n"
              "}")
    assert bibtex == Bibtex(full_record).format()

    full_record['creators'] = full_record['creators'][:1]
    bibtex = ("""@manual{doe_2014_12345,\n"""
              """  title        = {Test title},\n"""
              """  author       = {Doe, John},\n"""
              """  address      = {Staszkowka},\n"""
              """  month        = feb,\n"""
              """  year         = 2014,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()


def test_format_thesis(full_record):
    """Test."""
    full_record['resource_type']['subtype'] = 'thesis'
    bibtex = ("""@phdthesis{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title},\n"""
              """  school       = {I guess important},\n"""
              """  year         = 2014,\n"""
              """  address      = {Staszkowka},\n"""
              """  month        = feb,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()

    del full_record['imprint']
    bibtex = ("""@phdthesis{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title},\n"""
              """  school       = {I guess important},\n"""
              """  year         = 2014,\n"""
              """  month        = feb,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()


def test_format_unpublished(full_record):
    """Test."""
    full_record['resource_type']['subtype'] = 'preprint'
    bibtex = ("""@unpublished{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title},\n"""
              """  note         = {notes},\n"""
              """  month        = feb,\n"""
              """  year         = 2014,\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()
    full_record['resource_type']['subtype'] = 'workingpaper'
    assert bibtex == Bibtex(full_record).format()


def test_format_default_type(full_record):
    """Test."""
    full_record['resource_type']['type'] = 'undefined_type'
    bibtex = ("""@misc{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title},\n"""
              """  month        = feb,\n"""
              """  year         = 2014,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()


def test_format_publication_default(full_record):
    """Test."""
    full_record['resource_type']['subtype'] = 'undefined_subtype'
    full_record['resource_type']['type'] = 'publication'
    bibtex = ("""@misc{doe_2014_12345,\n"""
              """  author       = {Doe, John and\n"""
              """                  Doe, Jane and\n"""
              """                  Smith, John and\n"""
              """                  Nowak, Jack},\n"""
              """  title        = {Test title},\n"""
              """  month        = feb,\n"""
              """  year         = 2014,\n"""
              """  note         = {notes},\n"""
              """  doi          = {10.1234/foo.bar},\n"""
              """  url          = {https://doi.org/10.1234/foo.bar}\n"""
              """}""")
    assert bibtex == Bibtex(full_record).format()
