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
import warnings

depends_on = ['openaire_2013_05_02_pidstore']


def info():
    return "Migrate data to use user-zenodo identifier instead of curated"


def pre_upgrade():
    from invenio.search_engine import get_record, search_pattern, \
        get_fieldvalues
    from invenio.bibrecord import record_add_field
    from invenio.bibupload import bibupload


def do_upgrade():
    """ Implement your upgrades here  """

    from invenio.search_engine import search_pattern

    for recid in search_pattern(p="980__a:0->Z AND NOT 980__a:PROVISIONAL AND NOT 980__a:PENDING AND NOT 980__a:SPAM AND NOT 980__a:REJECTED AND NOT 980__a:DUPLICATE AND NOT 980__a:DARK AND NOT 980__c:DELETED AND NOT 980__a:OPENAIRE AND NOT 980__a:curated"):
        migrate_record(recid, additions=[[('a', 'provisional-user-zenodo')], ])

    for recid in search_pattern(p="980__a:curated"):
        migrate_record(recid, substitutions=[('curated', 'user-zenodo'), ])


def migrate_record(recid, substitutions=[], additions=[]):
    from invenio.search_engine import get_record
    from invenio.bibrecord import record_add_field
    from invenio.bibupload import bibupload
    from invenio.search_engine import get_fieldvalues

    rec = get_record(recid)

    if get_fieldvalues(recid, '536__c'):
        additions = additions + [[('a', 'user-ecfunded')], ]
    if recid == 941:
        additions = additions + [[('a', 'publication'), ('b', 'workingpaper')], ]

    for k in rec.keys():
        if k not in ['001', '980']:
            del rec[k]

    if substitutions:
        try:
            newcolls = []
            colls = rec['980']
            for c in colls:
                try:
                    # We are only interested in subfield 'a'
                    code, val = c[0][0]

                    for old, new in substitutions:
                        if val == old:
                            c[0][0] = (code, new)
                            break
                except IndexError:
                    pass
                newcolls.append(c)

            del rec['980']
            for c in newcolls:
                record_add_field(rec, '980', subfields=c[0])
        except KeyError:
            warnings.warn("Could not migrate record %s" % recid)
            return

    if additions:
        for a in additions:
            record_add_field(rec, '980', subfields=a)

    print rec

    bibupload(rec, opt_mode="correct")
