#!/usr/bin/env python
## This file is part of Invenio.
## Copyright (C) 2012 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Generate MARC XML file for correcting MARC field 8560_ (submitter)

Run as::
  python fix_8560.py > output.xml
  bibupload -c output.xml
"""
from invenio.flaskshell import db
from invenio.search_engine import search_pattern, get_fieldvalues
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.webuser import collect_user_info, get_uid_from_email
from invenio.openaire_deposit_engine import get_license_description, \
    get_project_description
from invenio.bibdocfile import download_external_url
import csv
import os
import codecs


HEADER = [
    'links', 'access_right', 'license', 'owner', 'type', 'doi',
    'publication_date', 'authors', 'title', 'conference_title',
    'conference_acronym', 'conference_dates', 'conference_place',
    'journal_title', 'journal_volume', 'journal_issue', 'journal_pages',
    'imprint_publisher', 'imprint_place', 'imprint_isbn', 'partof_title',
    'partof_pages', 'keywords', 'description',
]


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        yield row


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


def swap_name(x):
    names = x.split(" ")
    return "%s, %s" % (names[-1], " ".join(names[:-1]))


def map_row(row):
    row = dict(zip(HEADER, [c.strip() for c in row]))
    # Links
    row['links'] = [x.strip() for x in row['links'].split(" ")]
    #row['license'] = 'CC BY-NC-SA'
    # Owner
    if not row['owner']:
        row['owner'] = 'florida.estrella@cern.ch'
    # Type
    if row['type'] == 'Working paper':
        row['type'] = ('publication', 'workingpaper')
    elif row['type'] == 'Conference paper':
        row['type'] = ('publication', 'conferencepaper')
    elif row['type'] == 'Journal article':
        row['type'] = ('publication', 'article')
    elif row['type'] == 'Video':
        row['type'] = ('video', '')
    elif row['type'] == 'Presentation':
        row['type'] = ('presentation', '')
    elif row['type'] == 'Poster':
        row['type'] = ('poster', '')
    # Type
    row['authors'] = [swap_name(x).strip() for x in row['authors'].split(",")]
    row['keywords'] = filter(lambda x: x, [x.strip() for x in row['keywords'].split(";")])
    return row


def make_record(r, files):
    rec = {}
    # Owner
    record_add_field(rec, '856', ind1='0', subfields=[('f', r['owner']), ])
    # Access right
    record_add_field(rec, '542', subfields=[('l', r['access_right']), ])
    # Collection
    subfields = [('a', r['type'][0]), ]
    if r['type'][1]:
        subfields.append(('b', r['type'][1]))
    record_add_field(rec, '980', subfields=subfields)
    record_add_field(rec, '980', subfields=[('b', 'user_emi')])
    # Files
    fft_status = []
    if r['access_right'] == 'open':
        # Access to everyone
        fft_status = [
            'allow any',
        ]
    elif r['access_right'] in ('closed', 'restricted',):
        # Access to submitter, deny everyone else
        fft_status = [
            'allow email "%s"' % r['owner'],
            'deny all',
        ]
    fft_status = "firerole: %s" % "\n".join(fft_status)
    for file_path, real_name in files:
        record_add_field(rec, 'FFT', subfields=[
            ('a', file_path),
            #('d', 'some description') # TODO
            #('t', 'Type'), # TODO
            ('m', real_name),
            ('r', fft_status),
        ])
    # License
    if r['license'] == 'CC BY-NC-SA':
        record_add_field(rec, '540', subfields=[
            ('a', 'Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported'),
            ('u', 'http://creativecommons.org/licenses/by-nc-sa/3.0/'),
        ])
        record_add_field(rec, '650', ind1="1", ind2="7", subfields=[
            ('a', 'cc-nc'),
            ('2', 'opendefinition.org'),
        ])
    # DOI
    if r['doi']:
        record_add_field(rec, '024', '7', subfields=[('a', r['doi']), ('2', 'DOI')])
    # Publication date
    record_add_field(rec, '260', subfields=[('c', r['publication_date'])])
    # Title
    record_add_field(rec, '245', subfields=[('a', r['title'])])
    # Creators
    creators = r['authors']
    for (i, name) in enumerate(creators):
        if i == 0:
            field_no = '100'
        else:
            field_no = '700'
        subfields = [('a', name), ]
        record_add_field(rec, field_no, subfields=subfields)
    # Description
    if r['description']:
        record_add_field(rec, '520', subfields=[('a', r['description'])])
    # Project ID
    subfields = []
    project_description = get_project_description('261611')
    if project_description:
        subfields.append(('a', project_description))
    subfields.append(('c', str('261611')))
    record_add_field(rec, '536', subfields=subfields)
    # Keywords
    for keyword in r['keywords']:
        record_add_field(rec, '653', ind1="1", subfields=[('a', keyword)])
    # Journal
    subfields = []
    if r['journal_title']:
        subfields.append(('p', r['journal_title']))
        if r['publication_date']:
            year = r['publication_date'][:4]
            subfields.append(('y', year))
        if r.get('journal_issue'):
            subfields.append(('n', r['journal_issue']))
        if r.get('journal_volume'):
            subfields.append(('v', r['journal_volume']))
        if r.get('journal_pages'):
            subfields.append(('c', r['journal_pages']))
        if subfields:
            record_add_field(rec, '909', 'C', '4', subfields=subfields)
    # Book section
    if r.get('partof_title'):
        subfields = [('t', r.get('partof_title')), ('n', 'bookpart')]
        if r.get('partof_pages'):
            subfields.append(('g', r.get('partof_pages')))
        if r.get('imprint_publisher'):
            subfields.append(('b', r.get('imprint_publisher')))
        if r.get('imprint_place'):
            subfields.append(('a', r.get('imprint_place')))
        if r.get('imprint_isbn'):
            subfields.append(('z', r.get('imprint_isbn')))
        if r['publication_date']:
            year = r['publication_date'][:4]
            subfields.append(('c', year))
        record_add_field(rec, '773', '', '', subfields=subfields)
    # Conference
    conference_title = r.get('conference_title', '')
    conference_acronym = r.get('conference_acronym', '')
    conference_dates = r.get('conference_dates', '')
    conference_place = r.get('conference_place', '')
    conference_title = r.get('conference_title', '')
    conference_url = r.get('conference_url', '')
    if conference_title or conference_acronym or conference_url:
        meeting_values = [
            ('a', conference_title),
            ('g', conference_acronym),
            ('d', conference_dates),
            ('c', conference_place),
        ]

        subfields = []
        for code, val in meeting_values:
            if val:
                subfields.append((code, val))
        if subfields:
            record_add_field(rec, '711', '', '', subfields=subfields)
    return rec


def download_files(i, links):
    download_path = os.path.join(os.getcwd(), 'emi_files')
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    files = []
    for l in links:
        basename = os.path.basename(l)
        new_path = os.path.join(download_path, "%s_%s" % (i, basename))
        if not os.path.exists(new_path):
            tmp_path = download_external_url(l)
            os.rename(tmp_path, new_path)
        files.append((new_path, basename))
    return files


def handle_row(i, row):
    row = map_row(row)
    files = download_files(i, row['links'])
    record = make_record(row, files)
    return record


def main():
    """
    TODO: Fix file download of funny URLS ?conf...
    No keywords - check
    presentation pubype not shown for some reason.
    """
    f = codecs.open(os.path.expanduser("~/Desktop/emi.csv"), "r", "utf-8")

    print "<collection>"
    for (i, row) in enumerate(unicode_csv_reader(f)):
        if i == 0:
            continue
        try:
            print record_xml_output(handle_row(i, row))
        except Exception:
            pass
            #print e
            #print "Couldn't handle row:", i
    print "</collection>"
    f.close()


if __name__ == "__main__":
    main()
