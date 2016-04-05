# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""MARCXML translation index."""

from __future__ import absolute_import, print_function

from dateutil.parser import parse
from marshmallow import Schema, fields, post_dump


class RecordSchemaMARC(Schema):
    """Schema for records in MARC."""

    control_number = fields.Function(
        lambda o: str(o['metadata'].get('recid')))

    date_and_time_of_latest_transaction = fields.Function(
        lambda obj: parse(obj['updated']).strftime("%Y%m%d%H%M%S.0"))

    information_relating_to_copyright_status = fields.Function(
        lambda o: dict(copyright_status=o['metadata']['access_right']))

    index_term_uncontrolled = fields.Function(
        lambda o: dict(uncontrolled_term=o['metadata'].get('keywords'))
    )

    subject_added_entry_topical_term = fields.Function(
        lambda o: dict(
            topical_term_or_geographic_name_entry_element=o[
                'metadata'].get('license', {}).get('identifier'),
            source_of_heading_or_term=o[
                'metadata'].get('license', {}).get('source')
        ))

    terms_governing_use_and_reproduction_note = fields.Function(
        lambda o: dict(
            uniform_resource_identifier=o[
                'metadata'].get('license', {}).get('url'),
            terms_governing_use_and_reproduction=o[
                'metadata'].get('license', {}).get('license')
        ))

    title_statement = fields.Function(
        lambda o: dict(title=o['metadata'].get('title')))

    general_note = fields.Function(
        lambda o: dict(general_note=o['metadata'].get('notes')))

    information_relating_to_copyright_status = fields.Function(
        lambda o: dict(copyright_status=o['metadata'].get('access_right')))

    publication_distribution_imprint = fields.Function(
        lambda o: dict(
            date_of_publication_distribution=o['metadata'].get(
                'publication_date')))

    funding_information_note = fields.Function(
        lambda o: [dict(
            text_of_note=v.get('title'),
            grant_number=v.get('code')
        ) for v in o['metadata'].get('grants', [])])

    other_standard_identifier = fields.Function(
        lambda o: [dict(
            standard_number_or_code=v.get('identifier'),
            source_of_number_or_code=v.get('scheme'),
        ) for v in o['metadata'].get('alternate_identifiers', [])])

    added_entry_meeting_name = fields.Function(
        lambda o: [dict(
            meeting_name_or_jurisdiction_name_as_entry_element=v.get('title'),
            location_of_meeting=v.get('place'),
            date_of_meeting=v.get('dates'),
            miscellaneous_information=v.get('acronym'),
            number_of_part_section_meeting=v.get('session'),
            name_of_part_section_of_a_work=v.get('session_part'),
        ) for v in o['metadata'].get('meetings', [])])

    main_entry_personal_name = fields.Function(
        lambda o: [dict(
            personal_name=v.get('name'),
            affiliation=v.get('affiliation'),
            authority_record_control_number_or_standard_number=[
                "({0}){1}".format(scheme, identifier)
                for (scheme, identifier) in v.items()
                if identifier and scheme not in (
                    'name', 'affiliation', 'familyname', 'givennames')
            ],
        ) for v in o['metadata'].get('creators', [])]
    )

    added_entry_personal_name = fields.Function(
        lambda o: [dict(
            personal_name=v.get('name'),
            affiliation=v.get('affiliation'),
            relator_code=[
                "({0}){1}".format(scheme, identifier)
                for (scheme, identifier) in v.items()
                if identifier and scheme not in ('name', 'affiliation', 'type')
            ],
        ) for v in o['metadata'].get('contributors', [])]
    )

    summary = fields.Function(
        lambda o: dict(summary=o['metadata'].get('description')))

    host_item_entry = fields.Function(
        lambda o: [dict(
            relationship_information=v.get('relation'),
            note=v.get('scheme'),
        ) for v in o['metadata'].get('related_identifiers', [])])

    # Custom
    # ======

    resource_type = fields.Raw(attribute='metadata.resource_type')

    communities = fields.Raw(attribute='metadata.communities')

    references = fields.Raw(attribute='metadata.references')

    embargo_date = fields.Raw(attribute='metadata.embargo_date')

    _oai = fields.Raw(attribute='metadata._oai')

    @post_dump(pass_many=True)
    def remove_empty_fields(self, data, many):
        """Dump + Remove empty fields."""
        _filter_empty(data)
        return data


def _filter_empty(record):
    """Filter empty fields."""
    if isinstance(record, dict):
        for k in list(record.keys()):
            if record[k]:
                _filter_empty(record[k])
            if not record[k]:
                del record[k]
    elif isinstance(record, list) or isinstance(record, tuple):
        for (k, v) in list(enumerate(record)):
            if v:
                _filter_empty(record[k])
            if not v:
                del record[k]
