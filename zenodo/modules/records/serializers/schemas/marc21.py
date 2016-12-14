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
from flask import current_app
from marshmallow import Schema, fields, missing, post_dump


class RecordSchemaMARC21(Schema):
    """Schema for records in MARC."""

    control_number = fields.Function(
        lambda o: str(o['metadata'].get('recid')))

    date_and_time_of_latest_transaction = fields.Function(
        lambda obj: parse(obj['updated']).strftime("%Y%m%d%H%M%S.0"))

    information_relating_to_copyright_status = fields.Function(
        lambda o: dict(copyright_status=o['metadata']['access_right']))

    index_term_uncontrolled = fields.Function(
        lambda o: [
            dict(uncontrolled_term=kw)
            for kw in o['metadata'].get('keywords', [])
        ]
    )

    subject_added_entry_topical_term = fields.Method(
        'get_subject_added_entry_topical_term')

    terms_governing_use_and_reproduction_note = fields.Function(
        lambda o: dict(
            uniform_resource_identifier=o[
                'metadata'].get('license', {}).get('url'),
            terms_governing_use_and_reproduction=o[
                'metadata'].get('license', {}).get('title')
        ))

    title_statement = fields.Function(
        lambda o: dict(title=o['metadata'].get('title')))

    general_note = fields.Function(
        lambda o: dict(general_note=o['metadata'].get('notes')))

    information_relating_to_copyright_status = fields.Function(
        lambda o: dict(copyright_status=o['metadata'].get('access_right')))

    publication_distribution_imprint = fields.Method(
        'get_publication_distribution_imprint')

    funding_information_note = fields.Function(
        lambda o: [dict(
            text_of_note=v.get('title'),
            grant_number=v.get('code')
        ) for v in o['metadata'].get('grants', [])])

    other_standard_identifier = fields.Method('get_other_standard_identifier')

    added_entry_meeting_name = fields.Method('get_added_entry_meeting_name')

    main_entry_personal_name = fields.Method('get_main_entry_personal_name')

    added_entry_personal_name = fields.Method('get_added_entry_personal_name')

    summary = fields.Function(
        lambda o: dict(summary=o['metadata'].get('description')))

    host_item_entry = fields.Method('get_host_item_entry')

    dissertation_note = fields.Function(
        lambda o: dict(name_of_granting_institution=o[
            'metadata'].get('thesis', {}).get('university')))

    # Custom
    # ======

    resource_type = fields.Raw(attribute='metadata.resource_type')

    communities = fields.Raw(attribute='metadata.communities')

    references = fields.Raw(attribute='metadata.references')

    embargo_date = fields.Raw(attribute='metadata.embargo_date')

    journal = fields.Raw(attribute='metadata.journal')

    _oai = fields.Raw(attribute='metadata._oai')

    _files = fields.Method('get_files')

    leader = fields.Method('get_leader')

    conference_url = fields.Raw(attribute='metadata.meeting.url')

    def get_leader(self, o):
        """Return the leader information."""
        rt = o['metadata']['resource_type']['type']
        rec_types = {
            'image': 'two-dimensional_nonprojectable_graphic',
            'video': 'projected_medium',
            'dataset': 'computer_file',
            'software': 'computer_file',
        }
        type_of_record = rec_types[rt] if rt in rec_types \
            else 'language_material'
        res = {
            'record_length': '00000',
            'record_status': 'new',
            'type_of_record': type_of_record,
            'bibliographic_level': 'monograph_item',
            'type_of_control': 'no_specified_type',
            'character_coding_scheme': 'marc-8',
            'indicator_count': 2,
            'subfield_code_count': 2,
            'base_address_of_data': '00000',
            'encoding_level': 'unknown',
            'descriptive_cataloging_form': 'unknown',
            'multipart_resource_record_level':
                'not_specified_or_not_applicable',
            'length_of_the_length_of_field_portion': 4,
            'length_of_the_starting_character_position_portion': 5,
            'length_of_the_implementation_defined_portion': 0,
            'undefined': 0,
        }
        return res

    def get_files(self, o):
        """Get the files provided the record is open access."""
        if o['metadata']['access_right'] != 'open':
            return missing
        res = []
        for f in o['metadata'].get('_files', []):
            res.append(dict(
                uri=u'https://zenodo.org/record/{0}/files/{1}'.format(
                    o['metadata'].get('recid', ''), f['key']),
                size=f['size'],
                checksum=f['checksum'],
                type=f['type'],
            ))
        return res or missing

    def get_host_item_entry(self, o):
        """Get host items."""
        res = []
        for v in o['metadata'].get('related_identifiers', []):
            res.append(dict(
                main_entry_heading=v.get('identifier'),
                relationship_information=v.get('relation'),
                note=v.get('scheme'),
            ))

        imprint = o['metadata'].get('imprint', {})
        part_of = o['metadata'].get('part_of', {})
        if part_of and imprint:
            res.append(dict(
                main_entry_heading=imprint.get('place'),
                edition=imprint.get('publisher'),
                title=part_of.get('title'),
                related_parts=part_of.get('pages'),
                international_standard_book_number=imprint.get('isbn'),
            ))

        return res or missing

    def get_publication_distribution_imprint(self, o):
        """Get publication date and imprint."""
        res = []

        pubdate = o['metadata'].get('publication_date')
        if pubdate:
            res.append(dict(date_of_publication_distribution=pubdate))

        imprint = o['metadata'].get('imprint')
        part_of = o['metadata'].get('part_of')
        if not part_of and imprint:
            res.append(dict(
                place_of_publication_distribution=imprint.get('place'),
                name_of_publisher_distributor=imprint.get('publisher'),
                date_of_publication_distribution=pubdate,
            ))

        return res or missing

    def get_subject_added_entry_topical_term(self, o):
        """Get licenses and subjects."""
        res = []

        license = o['metadata'].get('license', {}).get('id')
        if license:
            res.append(dict(
                topical_term_or_geographic_name_entry_element='cc-by',
                source_of_heading_or_term='opendefinition.org',
                level_of_subject='Primary',
                thesaurus='Source specified in subfield $2',
            ))

        def _subject(term, id_, scheme):
            return dict(
                topical_term_or_geographic_name_entry_element=term,
                authority_record_control_number_or_standard_number=(
                    '({0}){1}'.format(scheme, id_)),
                level_of_subject='Primary',
            )

        for s in o['metadata'].get('subjects', []):
            res.append(_subject(
                s.get('term'), s.get('identifier'), s.get('scheme'), ))

        return res or missing

    def get_other_standard_identifier(self, o):
        """Get other standard identifiers."""
        res = []

        def stdid(pid, scheme, q=None):
            return dict(
                standard_number_or_code=pid,
                source_of_number_or_code=scheme,
                qualifying_information=q,
            )
        m = o['metadata']
        if m.get('doi'):
            res.append(stdid(m['doi'], 'doi'))

        for id_ in m.get('alternate_identifiers', []):
            res.append(stdid(
                id_.get('identifier'),
                id_.get('scheme'),
                q='alternateidentifier'
            ))

        return res or missing

    def _get_personal_name(self, v, relator_code=None):
        ids = []
        for scheme in ['gnd', 'orcid', ]:
            if v.get(scheme):
                ids.append((scheme, v[scheme]))

        return dict(
            personal_name=v.get('name'),
            affiliation=v.get('affiliation'),
            authority_record_control_number_or_standard_number=[
                "({0}){1}".format(scheme, identifier)
                for (scheme, identifier) in ids
            ],
            relator_code=[relator_code] if relator_code else []
        )

    def get_main_entry_personal_name(self, o):
        """Get main_entry_personal_name."""
        creators = o['metadata'].get('creators', [])
        if len(creators) > 0:
            v = creators[0]
            return self._get_personal_name(v)

    def get_added_entry_personal_name(self, o):
        """Get added_entry_personal_name."""
        items = []
        creators = o['metadata'].get('creators', [])
        if len(creators) > 1:
            for c in creators[1:]:
                items.append(self._get_personal_name(c))

        contributors = o['metadata'].get('contributors', [])
        for c in contributors:
            items.append(self._get_personal_name(
                c, relator_code=self._map_contributortype(c.get('type'))))

        supervisors = o['metadata'].get('thesis', {}).get('supervisors', [])
        for s in supervisors:
            items.append(self._get_personal_name(s, relator_code='ths'))

        return items

    def _map_contributortype(self, type_):
        return current_app.config['DEPOSIT_CONTRIBUTOR_DATACITE2MARC'][type_]

    def get_added_entry_meeting_name(self, o):
        """Get added_entry_meeting_name."""
        v = o['metadata'].get('meeting', {})
        return [dict(
            meeting_name_or_jurisdiction_name_as_entry_element=v.get('title'),
            location_of_meeting=v.get('place'),
            date_of_meeting=v.get('dates'),
            miscellaneous_information=v.get('acronym'),
            number_of_part_section_meeting=v.get('session'),
            name_of_part_section_of_a_work=v.get('session_part'),
        )]

    @post_dump(pass_many=True)
    def remove_empty_fields(self, data, many):
        """Dump + Remove empty fields."""
        _filter_empty(data)
        return data


def _is_non_empty(value):
    """Conditional for regarding a value as 'non-empty'.

    This enhances the default "bool" return value with some exceptions:
     - number 0 resolves as True - non-empty.
    """
    if isinstance(value, int):
        return True  # All integers are non-empty values
    else:
        return bool(value)


def _filter_empty(record):
    """Filter empty fields."""
    if isinstance(record, dict):
        for k in list(record.keys()):
            if _is_non_empty(record[k]):
                _filter_empty(record[k])
            if not _is_non_empty(record[k]):
                del record[k]
    elif isinstance(record, list) or isinstance(record, tuple):
        for (k, v) in list(enumerate(record)):
            if _is_non_empty(v):
                _filter_empty(record[k])
            if not _is_non_empty(v):
                del record[k]
