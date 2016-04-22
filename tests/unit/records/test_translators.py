# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""Unit tests for translators."""

from __future__ import absolute_import, print_function

from zenodo.modules.records.serializers.translators.legacy_to_zenodo import  \
    translate as translate_legacy_to_zenodo
from zenodo.modules.records.serializers.translators.zenodo_to_legacy import  \
    translate as translate_zenodo_to_legacy


def test_translators_legacy_zenodo_legacy():
    """Test the translator legacy_zenodo and zenodo_legacy."""
    test_data = dict(
        metadata=dict(
            access_right='embargoed',
            communities=[{'identifier': 'cfa'}],
            conference_acronym='Some acronym',
            conference_dates='Some dates',
            conference_place='Some place',
            conference_title='Some title',
            conference_url='http://someurl.com',
            conference_session='VI',
            conference_session_part='1',
            creators=[
                dict(name="Doe, John", affiliation="Atlantis",
                     orcid="0000-0002-1825-0097", gnd="170118215"),
                dict(name="Smith, Jane", affiliation="Atlantis")
            ],
            description="Some description",
            doi="10.1234/foo.bar",
            embargo_date="2010-12-09",
            grants=[dict(id="283595"), ],
            imprint_isbn="Some isbn",
            imprint_place="Some place",
            imprint_publisher="Some publisher",
            journal_issue="Some issue",
            journal_pages="Some pages",
            journal_title="Some journal name",
            journal_volume="Some volume",
            keywords=["Keyword 1", "keyword 2"],
            subjects=[
                dict(scheme="gnd", identifier="1234567899", term="Astronaut"),
                dict(scheme="gnd", identifier="1234567898", term="Amish"),
            ],
            license="cc-zero",
            notes="Some notes",
            partof_pages="SOme part of",
            partof_title="Some part of title",
            prereserve_doi=True,
            publication_date="2013-09-12",
            publication_type="book",
            references=[
                "Reference 1",
                "Reference 2",
            ],
            related_identifiers=[
                dict(identifier='10.1234/foo.bar2', relation='isCitedBy'),
                dict(identifier='10.1234/foo.bar3', relation='cites'),
                dict(
                    identifier='2011ApJS..192...18K',
                    relation='isAlternativeIdentifier'),
            ],
            thesis_supervisors=[
                dict(name="Doe Sr., John", affiliation="Atlantis"),
                dict(name="Smith Sr., Jane", affiliation="Atlantis",
                     orcid="http://orcid.org/0000-0002-1825-0097",
                     gnd="http://d-nb.info/gnd/170118215")
            ],
            thesis_university="Some thesis_university",
            contributors=[
                dict(name="Doe Sr., Jochen", affiliation="Atlantis",
                     type="Other"),
                dict(name="Smith Sr., Marco", affiliation="Atlantis",
                     orcid="http://orcid.org/0000-0002-1825-0097",
                     gnd="http://d-nb.info/gnd/170118215",
                     type="DataCurator")
            ],
            title="Test title",
            upload_type="publication",
        )
    )
    zenodo_record = translate_legacy_to_zenodo(test_data)
    legacy_record = translate_zenodo_to_legacy(zenodo_record)
    assert test_data == legacy_record


def test_translators_legacy_zenodo_legacy_unicode():
    """Test the translator legacy_zenodo and zenodo_legacy using unicode."""
    test_data = dict(
        metadata=dict(
            access_right='restricted',
            access_conditions='Αυτή είναι μια δοκιμή',
            communities=[{'identifier': 'cfa'}],
            conference_acronym='Αυτή είναι μια δοκιμή',
            conference_dates='هذا هو اختبار',
            conference_place='Սա փորձություն',
            conference_title='Гэта тэст',
            conference_url='http://someurl.com',
            conference_session='5',
            conference_session_part='a',
            creators=[
                dict(name="Doe, John", affiliation="Това е тест"),
                dict(name="Smith, Jane", affiliation="Tio ĉi estas testo")
            ],
            description="这是一个测试",
            doi="10.1234/foo.bar",
            embargo_date="2010-12-09",
            grants=[dict(id="283595"), ],
            imprint_isbn="Some isbn",
            imprint_place="這是一個測試",
            imprint_publisher="ეს არის გამოცდა",
            journal_issue="આ એક કસોટી છે",
            journal_pages="זהו מבחן",
            journal_title="यह एक परीक्षण है",
            journal_volume="Þetta er prófun",
            keywords=["これはテストです", "ಇದು ಪರೀಕ್ಷೆ"],
            subjects=[
                dict(scheme="gnd", identifier="1234567899", term="これはです"),
                dict(scheme="gnd", identifier="1234567898", term="ಇ"),
            ],
            license="cc-zero",
            notes="이것은 테스트입니다",
            partof_pages="ນີ້ແມ່ນການທົດສອບ",
            partof_title="ही चाचणी आहे",
            prereserve_doi=True,
            publication_date="2013-09-12",
            publication_type="book",
            related_identifiers=[
                dict(
                    identifier='2011ApJS..192...18K',
                    relation='isAlternativeIdentifier'),
                dict(identifier='10.1234/foo.bar2', relation='isCitedBy'),
                dict(identifier='10.1234/foo.bar3', relation='cites'),
            ],
            thesis_supervisors=[
                dict(name="Doe Sr., این یک تست است", affiliation="Atlantis"),
                dict(name="Это Sr., Jane", affiliation="Atlantis")
            ],
            thesis_university="இந்த ஒரு சோதனை",
            contributors=[
                dict(name="Doe Sr.,  ن یک تست", affiliation="Atlantis",
                     type="Other"),
                dict(name="SmЭтith Sr., Marco", affiliation="Atlantis",
                     type="DataCurator")
            ],
            title="Đây là một thử nghiệm",
            upload_type="publication",
        )
    )
    zenodo_record = translate_legacy_to_zenodo(test_data)
    legacy_record = translate_zenodo_to_legacy(zenodo_record)
    assert test_data == legacy_record
