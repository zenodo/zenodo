# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

import warnings
from sqlalchemy import *
from invenio.ext.sqlalchemy import db
from invenio.modules.upgrader.api import op
from invenio.utils.text import wait_for_user


depends_on = [u'zenodo_2015_06_10_missing_formats']


def has_two_dois(fields):
    res = 0
    for field, data in fields.items():
        if data['0247_2'] == 'DOI':
            res += 1
    return res > 1


def info():
    return "Short description of upgrade displayed to end-user"


def do_upgrade():
    """Implement your upgrades here."""
    result = db.engine.execute("""
        select b.id, d.tag, d.value, r.field_number
        from bibrec as b join bibrec_bib02x as r on b.id=r.id_bibrec join bib02x as d on r.id_bibxxx=d.id
        where b.id in (
            select b.id
            from bibrec as b join bibrec_bib02x as r on b.id=r.id_bibrec join bib02x as d on r.id_bibxxx=d.id
            where d.tag='0247_2'
            group by b.id having count(d.tag) > 1
        )
        order by b.id, r.field_number;""")

    records = {}

    for r in result:
        recid = str(r[0])
        tag = r[1]
        value = r[2]
        fieldno = str(r[3])

        if recid not in records:
            records[recid] = {}
        if fieldno not in records[recid]:
            records[recid][fieldno] = {}
        if tag not in records[recid][fieldno]:
            records[recid][fieldno][tag] = value


    recdata = {}

    # Determine doi and alternate identifiers.
    for recid, fields in records.items():
        recdata[recid] = dict(doi=None, alt=[])

        if not has_two_dois(fields):
            for field, data in fields.items():
                if data['0247_2'] == 'DOI':
                    recdata[recid]['doi'] = data['0247_a']
                else:
                    recdata[recid]['alt'].append(
                        {"id": data['0247_a'].strip(), "scheme": data['0247_2']}
                    )
        else:
            dois = []
            alt = []


            for data in fields.values():
                if data['0247_2'].lower() == 'doi':
                    dois.append(data['0247_a'].strip())
                else:
                    recdata[recid]['alt'].append(
                        {"id": data['0247_a'].strip(), "scheme": data['0247_2']}
                    )

            dois = set(dois)
            for d in dois:
                if d.startswith("10.5281"):
                    recdata[recid]['doi'] = d
                else:
                    recdata[recid]['alt'].append({'id': d, 'scheme': 'doi'})

    from invenio.legacy.bibupload.utils import open_temp_file, close_temp_file
    from invenio.legacy.bibsched.bibtask import task_low_level_submission

    (fo, fname) = open_temp_file("datafix")


    fo.write("<collection>\n")
    for recid, data in recdata.items():
        fo.write("<record>\n")
        fo.write("""   <controlfield tag="001">%s</controlfield>\n""" % recid)

        fo.write("""   <datafield tag="024" ind1="7" ind2=" ">
        <subfield code="2">DOI</subfield>
        <subfield code="a">%s</subfield>
    </datafield>\n""" % data['doi'])

        for alt in data['alt']:
            fo.write("""   <datafield tag="024" ind1="7" ind2=" ">
        <subfield code="2">%s</subfield>
        <subfield code="a">%s</subfield>
        <subfield code="q">alternateIdentifier</subfield>
    </datafield>\n""" % (alt['scheme'], alt['id']))

        fo.write("</record>\n")

    fo.write("</collection>\n")

    close_temp_file(fo, fname)

    task_low_level_submission('bibupload', "datafix", "-c", fname)


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1


def pre_upgrade():
    """Run pre-upgrade checks (optional)."""
    # Example of raising errors:
    # raise RuntimeError("Description of error 1", "Description of error 2")


def post_upgrade():
    """Run post-upgrade checks (optional)."""
    # Example of issuing warnings:
    # warnings.warn("A continuable error occurred")
