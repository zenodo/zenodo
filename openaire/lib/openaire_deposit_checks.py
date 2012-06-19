## This file is part of Invenio.
## Copyright (C) 2010, 2011, 2012 CERN.
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
Metadata field validators
"""

from cgi import escape
import re
import time

from invenio.openaire_deposit_config import CFG_ACCESS_RIGHTS, \
    CFG_OPENAIRE_PUBLICATION_TYPES


# Regular expressions
_RE_AUTHOR_ROW = re.compile(u'^\w{2,}(\s+\w{2,})*\s*,\s*(\w{2,}|\w\.)(\s+\w{1,}|\s+\w\.)*\s*(:\s*\w{2,}.*)?$', re.U)
_RE_PAGES = re.compile('\d+(-\d+)?')
_RE_DOI = re.compile("(doi:)?10\.\d+(.\d+)*/.*", re.I)

def _check_title(metadata, ln, _):
    title = metadata.get('title', '')
    title = title.strip()
    if not title:
        return ('title', 'error', [_('The title field of the Publication is mandatory but is currently empty')])
    elif title:
        title = title.decode('UTF8')
        uppers = 0
        for c in title:
            if c.isupper():
                uppers += 1
        if 1.0 * uppers / len(title) > 0.75:
            return ('title', 'warning', [_('The title field of the Publication seems to be written all in UPPERCASE')])
        elif title.islower():
            return ('title', 'warning', [_('The title field of the Publication seems to be written all in lowercase. Was this intentional?')])


def _check_original_title(metadata, ln, _):
    title = metadata.get('original_title', '')
    title = title.decode('UTF8')
    if title:
        uppers = 0
        for c in title:
            if c.isupper():
                uppers += 1
        if 1.0 * uppers / len(title) > 0.75:
            return ('original_title', 'warning', [_('The original title field of the Publication seems to be written all in UPPERCASE')])

def _check_keywords(metadata, ln, _):
    keywords = metadata.get('keywords', '')
    keywords = keywords.decode('UTF8')
    if keywords:
        for keyword in keywords.splitlines():
            keyword = keyword.strip()
            if keyword:
                count_dash = 0
                warn = False
                for c in keyword:
                    if c == ";":
                        warn = True
                        break
                    elif c == ",":
                        warn = True
                        break
                    elif c == "-":
                        count_dash += 1
                        if count_dash >= 2:
                            warn=True
                            break
                
                if warn:
                    return ('keywords', 'warning', [_('Please ensure that you have only one keyword/phrase per line.')])


def _check_authors(metadata, ln, _):
    authors = metadata.get('authors', '')
    authors = authors.decode('UTF8')
    if not authors.strip():
        return ('authors', 'error', [_('The authorship of the Publication is a mandatory field but is currently empty')])
    errors = []
    warnings = []
    for row in authors.split('\n'):
        row = row.strip()
        if row:
            if not _RE_AUTHOR_ROW.match(row):
                if not ',' in row:
                    errors.append(_("""<strong>"%(row)s"</strong? is not a well formatted authorship (correct format is <em>"Last Names, First Names"</em> or <em>"Last Names, First Names: Affiliation"<em> but a <em>","</em> separating <em>"Last Names"</em> and <em>"First Names"</em> does not seem to exist).""" % {"row": escape(row.encode('UTF8'))}))
                else:
                    errors.append(_("""<strong>"%(row)s"</strong> is not a well formatted authorship (correct format is <em>"Last Names, First Names"</em> or <em>"Last Names, First Names: Affiliation"</em>).""" % {"row": escape(row.encode('UTF8'))}))
            if not ':' in row:
                warnings.append(_("""You have not specified an affiliation for <strong>"%(row)s"</strong> but an affiliation is recommended.""" % {"row": escape(row.encode('UTF8'))}))
                if row.islower():
                    warnings.append(_("""It seems that the author name <strong>"%(row)s"</strong> has been written all lower case. Was this intentional?""") % {"row": escape(row.encode('UTF8'))})
            else:
                name, affiliation = row.split(":", 1)
                if name.islower():
                    warnings.append(_("""It seems that the author name <strong>"%(name)s"</strong> for the authorship <strong>"%(row)s"</strong> has been written all lower case. Was this intentional?""") % {"name": escape(name.encode('UTF8')), "row": escape(row.encode('UTF8'))})
                if affiliation.islower():
                    warnings.append(_("""It seems that the affiliation <strong>"%(affiliation)s"</strong> for the authorship <strong>"%(row)s"</strong> has been written all lower case. Was this intentional?""") % {"affiliation": escape(affiliation.encode('UTF8')), "row": escape(row.encode('UTF8'))})
                if name.isupper():
                    warnings.append(_("""It seems that the author name <strong>"%(name)s"</strong> for the authorship <strong>"%(row)s"</strong> has been written all upper case. Was this intentional?""") % {"name": escape(name.encode('UTF8')), "row": escape(row.encode('UTF8'))})
    if errors:
        return ('authors', 'error', errors)
    elif warnings:
        return ('authors', 'warning', warnings)


def _check_abstract(metadata, ln, _):
    abstract = metadata.get('abstract', '')
    if not abstract.strip():
        return ('abstract', 'error', [_('The abstract of the Publication is a mandatory field but is currently empty')])


def _check_language(metadata, ln, _):
    language = metadata.get('language', '')
    if not language.strip():
        return ('language', 'error', [_('The language of the Publication is a mandatory field but is currently empty')])


def _check_access_rights(metadata, ln, _):
    access_rights = metadata.get('access_rights', '')
    if not access_rights in CFG_ACCESS_RIGHTS(ln):
        return ('access_rights', 'error', [_('The access rights field of the Publication is not set to one of the expected values')])


def _check_embargo_date(metadata, ln, _):
    access_rights = metadata.get('access_rights', '')
    embargo_date = metadata.get('embargo_date', '')
    if access_rights == 'embargoedAccess':
        if not embargo_date:
            return ('embargo_date', 'error', [_('The embargo end date is mandatory when the Access rights field of the Publication is set to Embargo access')])
        try:
            time.strptime(embargo_date, '%Y-%m-%d')
        except ValueError:
            return ('embargo_date', 'error', [_('The access rights of the Publication is set to Embargo access but a valid embargo end date is not set (correct format is YYYY-MM-DD)')])


def _check_publication_date(metadata, ln, _):
    publication_date = metadata.get('publication_date', '')
    if not publication_date.strip():
        return ('publication_date', 'error', [_('The publication date is mandatory')])
    try:
        time.strptime(publication_date, '%Y-%m-%d')
    except ValueError:
        return ('publication_date', 'error', [_('The publication date is not correctly typed (correct format is YYYY-MM-DD)')])


def _check_pages(metadata, ln, _):
    pages = metadata.get('pages', '').strip()
    if pages and not _RE_PAGES.match(pages):
        return ('pages', 'error', [_("The pages are not specified correctly")])


def _check_pages_no(metadata, ln, _):
    pages = metadata.get('report_pages_no', '').strip()
    if pages:
        try:
            int(pages)
        except ValueError:
            return ('report_pages_no', 'error', [_("The number of pages are not specified correctly")])


def _check_doi(metadata, ln, _):
    doi = metadata.get('doi', '').strip()
    if doi:
        if not _RE_DOI.match(doi):
            return ('doi', 'error', [_('The provided DOI is not correctly typed: you entered "%s" but it should look similar to "10.1234/foo-bar"' % escape(doi, True))])
    else:
        return ('doi', 'warning', [_("If possible, please provide the digital object identifier (DOI) assigned by the publisher to your publication")])


def _check_publication_type(metadata, ln, _):
    publication_type = metadata.get('publication_type', '')
    if not publication_type in CFG_OPENAIRE_PUBLICATION_TYPES(ln):
        return ('publication_type', 'error', [_('The document type field of the Publication is not set to one of the expected values')])


def _check_accept_cc0_license(metadata, ln, _):
    publication_type = metadata.get('publication_type', '')
    if publication_type == 'data':
        accept = metadata.get('accept_cc0_license', '')
        if accept != 'yes':
            return ('accept_cc0_license', 'error', [_("You must agree to release your data under CC0.")])

def _check_related_publications(metadata, ln, _):
    publication_type = metadata.get('publication_type', '')
    if publication_type == 'data':
        pubs = metadata.get('related_publications', '')
        pubs = pubs.decode('UTF8')
        
        found = False
        for doi in pubs.splitlines():
            doi = doi.strip()
            if doi:
                if _RE_DOI.match(doi):
                    found = True 
                else:
                    return ('related_publications', 'error', [_('The provided DOI is not correctly typed: you entered "%s" but it should look similar to "10.1234/foo-bar"' % escape(doi, True))])
        
        if not found:
            return ('related_publications', 'error', [_('You must provide at least one DOI.')])
 


CFG_METADATA_FIELDS_CHECKS = {
    'title': _check_title,
    'original_title': _check_original_title,
    'authors': _check_authors,
    'abstract': _check_abstract,
    'language': _check_language,
    'access_rights': _check_access_rights,
    'embargo_date': _check_embargo_date,
    'publication_date': _check_publication_date,
    'pages': _check_pages,
    'doi': _check_doi,
    'publication_type': _check_publication_type,
    'report_pages_no': _check_pages_no,
    'keywords' : _check_keywords,
    'accept_cc0_license' : _check_accept_cc0_license,
    'related_publications' : _check_related_publications,
}
"""
Dictionary of metadata field validator functions.
"""
