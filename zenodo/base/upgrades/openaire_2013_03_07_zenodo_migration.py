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

import warnings
from invenio.legacy.dbquery import run_sql
from invenio.utils.text import wait_for_user


depends_on = ['openaire_2013_03_03_license_data']

collection_mapping = {
    'BACHELORTHESIS': ('publication', 'thesis'),
    'BOOK': ('publication', 'book'),
    'PREPRINT': ('publication', 'preprint'),
    'BOOKPART': ('publication', 'section'),
    'DATA': ('dataset', ''),
    'MEETING_CONFERENCEPAPER': ('publication', 'conferencepaper'),
    'MEETING_POSTER': ('poster', ''),
    'MEETING_PROCEEDINGSARTICLE': ('publication', 'conferencepaper'),
    'MEETING_PROCEEDINGARTICLE': ('publication', 'conferencepaper'),
    'OPENAIRE': ('publication', 'article'),
    'REPORT_OTHER': ('publication', 'report'),
    'REPORT_PROJECTDELIVERABLE': ('publication', 'report'),
    'WORKINGPAPER': ('publication', 'workingpaper'),
}

newcolls = ['publication', 'poster', 'presentation', 'dataset', 'image',
    'video', ]

newsubcolls = ['book', 'section', 'conferencepaper', 'article', 'patent',
    'preprint', 'report', 'thesis', 'technicalnote', 'workingpaper', 'other',
    'figure', 'plot', 'drawing', 'diagram', 'photo', 'other', ]


def migrate_980__ab(recid, rec):
    from invenio.bibrecord import record_add_field
    from invenio.search_engine import get_fieldvalues

    collections = get_fieldvalues(recid, "980__a")
    subcollections = get_fieldvalues(recid, "980__b")

    upload_type = []
    extras = []
    curated = True

    for val in collections:
        if val in ['DARK', 'DELETED', 'DUPLICATE', 'PENDING', 'REJECTED', 'PROVISIONAL', ]:
            curated = False
            extras.append(val)
        if val in collection_mapping:
            upload_type.append(collection_mapping[val])
        elif val in newcolls:
            upload_type.append(val)

    for val in subcollections:
        if val in collection_mapping:
            upload_type.append(collection_mapping[val])
        elif val in newsubcolls:
            upload_type.append(val)

    if upload_type:
        upload_type = [upload_type[0]]

    is_public = False
    if curated:
        upload_type.append(('curated', ''))
        is_public = True

    for a, b in upload_type:
        if b:
            record_add_field(rec, '980', subfields=[('a', a), ('b', b)])
        else:
            record_add_field(rec, '980', subfields=[('a', a), ])
    if extras:
        for e in extras:
            record_add_field(rec, '980', subfields=[('a', e), ])
    return (rec, is_public)


def migrate_542__l(recid, rec):
    from invenio.bibrecord import record_add_field
    from invenio.search_engine import get_fieldvalues

    val = get_fieldvalues(recid, "542__l")

    if val and val[0]:
        newval = ''
        if val[0] == 'OPEN':
            newval = 'open'
        elif val[0] == 'RESTRICTED':
            newval = 'restricted'
        elif val[0] == 'openAccess':
            newval = 'open'
        elif val[0] == 'closedAccess':
            newval = 'closed'
        elif val[0] == 'embargoedAccess':
            newval = 'embargoed'
        elif val[0] == 'restrictedAccess':
            newval = 'restricted'
        elif val[0] == 'cc0':
            newval = 'open'
            record_add_field(rec, '540', subfields=[('a', 'Creative Commons CCZero'), ('u', 'http://www.opendefinition.org/licenses/cc-zero')])
            record_add_field(rec, '650', ind1="1", ind2="7", subfields=[
                ('a', 'cc-zero'),
                ('2', 'opendefinition.org'),
            ])
        if newval:
            record_add_field(rec, '542', subfields=[('l', newval)])
            return (rec, newval)
        else:
            return (rec, val[0])
    return (rec, "closed")


def migrate_bibdoc_status(recid, is_public, access_right):
    from invenio.search_engine import get_fieldvalues
    from invenio.bibdocfile import BibRecDocs

    # Generate firerole
    fft_status = []
    if is_public:
        email = get_fieldvalues(recid, "8560_f")[0]
        if access_right == 'open':
            # Access to everyone
            fft_status = [
                'allow any',
            ]
        elif access_right == 'embargoed':
            # Access to submitted, Deny everyone else until embargo date,
            # then allow all
            date = get_fieldvalues(recid, "942__a")[0]
            fft_status = [
                'allow email "%s"' % email,
                'deny until "%s"' % date,
                'allow any',
            ]
        elif access_right in ('closed', 'restricted',):
            # Access to submitter, deny everyone else
            fft_status = [
                'allow email "%s"' % email,
                'deny all',
            ]
    else:
        # Access to submitter, deny everyone else
        fft_status = None

    if fft_status:
        fft_status = "firerole: %s" % "\n".join(fft_status)

        brd = BibRecDocs(recid)
        for d in brd.list_bibdocs():
            d.set_status(fft_status)


def migrate_record(recid):
    """
    Migrate a record from Orphan to ZENODO
    """
    from invenio.bibrecord import record_add_field
    from invenio.bibupload import bibupload

    rec = {}
    record_add_field(rec, '001', controlfield_value=str(recid))

    (rec, is_public) = migrate_980__ab(recid, rec)
    (rec, accessright) = migrate_542__l(recid, rec)
    migrate_bibdoc_status(recid, is_public, accessright)

    bibupload(rec, opt_mode="correct")


def info():
    return "Orphan to ZENODO migration"


def do_upgrade():
    from invenio.search_engine import search_pattern

    recids = search_pattern(p="0->Z")
    for recid in recids:
        migrate_record(recid)


def estimate():
    """  Estimate running time of upgrade in seconds (optional). """
    return 20


def pre_upgrade():
    """  Run pre-upgrade checks (optional). """
    from invenio.bibupload import bibupload
    from invenio.search_engine import search_pattern, get_fieldvalues
    from invenio.bibrecord import record_add_field


def post_upgrade():
    """  Run post-upgrade checks (optional). """
    # Example of issuing warnings:
    # warnings.warn("A continuable error occurred")
