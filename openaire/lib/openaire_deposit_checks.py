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

from invenio.openaire_deposit_config import CFG_ACCESS_RIGHTS_KEYS, \
    CFG_OPENAIRE_PUBLICATION_TYPES_KEYS, CFG_OPENAIRE_REPORT_TYPES_KEYS, \
    CFG_OPENAIRE_THESIS_TYPES_KEYS
from invenio.validators import is_isbn, is_all_uppercase, is_probably_list, \
    is_issn


def explode_values(val, check_func, stop_on_error=True):
    """ """
    errors = []
    warnings = []

    for row in val.splitlines():
        row = row.strip()
        errs, warns = check_func(row)
        if stop_on_error and errs:
            return

# Regular expressions
_RE_AUTHOR_ROW = re.compile(u'^\w{2,}(\s+\w{2,})*\s*,\s*(\w{2,}|\w\.)(\s+\w{1,}|\s+\w\.)*\s*(:\s*\w{2,}.*)?$', re.U)
_RE_PAGES = re.compile('\d+(-\d+)?')
_RE_DOI = re.compile("(doi:)?10\.\d+(.\d+)*/.*", re.I)


def _get_publication_type(metadata):
    """ Get the publication type of the currently deposited """
    return metadata.get('publication_type', '')


def _check_text(metadata, ln, _, field):
    title = metadata.get(field, '')
    title = title.strip()
    if not title:
        return (field, 'error', [_('The field is mandatory but is currently empty')])
    elif title:
        title = title.decode('UTF8')
        if is_all_uppercase(title):
            return (field, 'warning', [_('The field seems to be written all in UPPERCASE. Was this intentional?')])
        elif title.islower():
            return (field, 'warning', [_('The field seems to be written all in lowercase. Was this intentional?')])


def _check_title(metadata, ln, _):
    return _check_text(metadata, ln, _, 'title')


def _check_university(metadata, ln, _):
    return _check_text(metadata, ln, _, 'university')


def _check_original_title(metadata, ln, _):
    title = metadata.get('original_title', '')
    title = title.decode('UTF8')
    if title:
        if is_all_uppercase(title):
            return ('original_title', 'warning', [_('The original title field of the publication seems to be written all in UPPERCASE')])


def _check_keywords(metadata, ln, _):
    keywords = metadata.get('keywords', '')
    keywords = keywords.decode('UTF8')
    if keywords:
        for keyword in keywords.splitlines():
            keyword = keyword.strip()
            if is_probably_list(keyword):
                return ('keywords', 'warning', [_('Please ensure that you have only one keyword/phrase per line.')])


def _check_names(field, metadata, ln, _, mandatory=True):
    names = metadata.get(field, '')
    names = names.decode('UTF8')
    if mandatory and not names.strip():
        return (field, 'error', [_('The field is a mandatory field but is currently empty')])
    errors = []
    warnings = []
    for row in names.splitlines():
        row = row.strip()
        if row:
            if not _RE_AUTHOR_ROW.match(row):
                if not ',' in row:
                    errors.append(_("""<strong>"%(row)s"</strong> is missing a comma separating last name and first name. The format is <em>"Last name, First name: Institution (optional)"</em>.""" % {"row": escape(row.encode('UTF8'))}))
                else:
                    errors.append(_("""<strong>"%(row)s"</strong> is not well-formatted. The format is <em>"Last name, First name: Institution (optional)"</em>.""" % {"row": escape(row.encode('UTF8'))}))
            if not ':' in row:
                warnings.append(_("""You have not specified an affiliation for <strong>"%(row)s"</strong> but an affiliation is recommended. The format is <em>"Last name, First name: Institution (optional)"</em>.""" % {"row": escape(row.encode('UTF8'))}))
                if row.islower():
                    warnings.append(_("""It seems that the name <strong>"%(row)s"</strong> has been written all lower case. Was this intentional?""") % {"row": escape(row.encode('UTF8'))})
            else:
                name, affiliation = row.split(":", 1)
                if name.islower():
                    warnings.append(_("""It seems that the name <strong>"%(name)s"</strong> in <strong>"%(row)s"</strong> has been written all lower case. Was this intentional?""") % {"name": escape(name.encode('UTF8')), "row": escape(row.encode('UTF8'))})
                if affiliation.islower():
                    warnings.append(_("""It seems that the affiliation <strong>"%(affiliation)s"</strong> in <strong>"%(row)s"</strong> has been written all lower case. Was this intentional?""") % {"affiliation": escape(affiliation.encode('UTF8')), "row": escape(row.encode('UTF8'))})
                if name.isupper():
                    warnings.append(_("""It seems that the name <strong>"%(name)s"</strong> in <strong>"%(row)s"</strong> has been written all upper case. Was this intentional?""") % {"name": escape(name.encode('UTF8')), "row": escape(row.encode('UTF8'))})
                if ':' in affiliation:
                    warnings.append(_("""Please ensure you only have one name per line.""") % {"name": escape(name.encode('UTF8')), "row": escape(row.encode('UTF8'))})
    if errors:
        return (field, 'error', errors)
    elif warnings:
        return (field, 'warning', warnings)


def _check_authors(metadata, ln, _):
    return _check_names('authors', metadata, ln, _)


def _check_supervisors(metadata, ln, _):
    return _check_names('supervisors', metadata, ln, _, mandatory=False)


def _check_abstract(metadata, ln, _):
    abstract = metadata.get('abstract', '')
    if not abstract.strip():
        return ('abstract', 'error', [_('The abstract of the publication is a mandatory field but is currently empty')])


def _check_language(metadata, ln, _):
    language = metadata.get('language', '')
    if not language.strip():
        return ('language', 'error', [_('The language of the publication is a mandatory field but is currently empty')])


def _check_access_rights(metadata, ln, _):
    access_rights = metadata.get('access_rights', '')
    if not access_rights in CFG_ACCESS_RIGHTS_KEYS:
        return ('access_rights', 'error', [_('The access rights field of the publication is not set to one of the expected values')])


def _check_embargo_date(metadata, ln, _):
    publication_type = _get_publication_type(metadata)
    if publication_type != 'data':
        access_rights = metadata.get('access_rights', '')
        embargo_date = metadata.get('embargo_date', '')
        if access_rights == 'embargoedAccess':
            if not embargo_date:
                return ('embargo_date', 'error', [_('The embargo end date is mandatory when the access rights field of the publication is set to embargoed access')])
            try:
                time.strptime(embargo_date, '%Y-%m-%d')
            except ValueError:
                return ('embargo_date', 'error', [_('The access rights of the publication is set to embargo access but a valid embargo end date is not set (correct format is YYYY-MM-DD)')])


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
    publication_type = _get_publication_type(metadata)
    if not publication_type in CFG_OPENAIRE_PUBLICATION_TYPES_KEYS:
        return ('publication_type', 'error', [_('The document type field of the publication is not set to one of the expected values')])


def _check_accept_cc0_license(metadata, ln, _):
    publication_type = _get_publication_type(metadata)
    if publication_type == 'data':
        accept = metadata.get('accept_cc0_license', '')
        if accept != 'yes':
            return ('accept_cc0_license', 'error', [_("You must agree to release your data under CC0.")])


def _check_related_dois(field, metadata, ln, _, title):
    dois = metadata.get(field, '')
    dois = dois.decode('UTF8')

    # Object DOI
    main_doi = metadata.get('doi', '').strip()
    if main_doi and _RE_DOI.match(main_doi):
        if main_doi.startswith("doi:"):
            main_doi = main_doi[4:]
    else:
        main_doi = None

    for doi in dois.splitlines():
        doi = doi.strip()
        if doi:
            if not _RE_DOI.match(doi):
                return (field, 'error', [_('The provided DOI is not correctly typed: you entered "%s" but it should look similar to "10.1234/foo-bar"' % escape(doi, True))])
            elif main_doi:
                if doi.startswith("doi:"):
                    doi = doi[4:]
                if main_doi == doi:
                    return (field, 'error', [_('The provided DOI "%s" must not be identical to the DOI provided as identifier of the %s"' % (escape(doi, True), title))])


def _check_related_publications(metadata, ln, _):
    return _check_related_dois('related_publications', metadata, ln, _, _("dataset"))


def _check_related_datasets(metadata, ln, _):
    return _check_related_dois('related_datasets', metadata, ln, _, _("publication"))


def _check_type(metadata, ln, _, pubtype, allowed_values):
    publication_type = metadata.get('publication_type', '')
    if publication_type == pubtype:
        type_val = metadata.get('%s_type' % pubtype, '')
        if not type_val in allowed_values:
            return ('%s_type' % pubtype, 'error', [_('The field is not set to one of the expected values')])


def _check_report_type(metadata, ln, _):
    return _check_type(metadata, ln, _, 'report', CFG_OPENAIRE_REPORT_TYPES_KEYS)


def _check_thesis_type(metadata, ln, _):
    return _check_type(metadata, ln, _, 'thesis', CFG_OPENAIRE_THESIS_TYPES_KEYS)


def _check_extra_report_numbers(metadata, ln, _):
    val = metadata.get('extra_report_numbers', '')
    val = val.decode('UTF8')
    for row in val.splitlines():
        row = row.strip()
        if is_probably_list(row, separators=[';', ',']):
            return ('extra_report_numbers', 'warning', [_('Please ensure that you have only one report number per line.')])


def _check_isbn(metadata, ln, _):
    val = metadata.get('isbn', '').strip()
    if val and not is_isbn(val.strip()):
        return ('isbn', 'error', [_('\'%s\' is not a valid ISBN-10 or ISBN-13 number.' % val)])


def _check_issn(metadata, ln, _):
    val = metadata.get('issn', '').strip()
    if val and not is_issn(val.strip()):
        return ('issn', 'error', [_('\'%s\' is not a valid ISSN number.' % val)])


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
    'keywords': _check_keywords,
    'accept_cc0_license': _check_accept_cc0_license,
    'related_publications': _check_related_publications,
    'related_datasets': _check_related_datasets,
    #'publisher' : _check_publisher,
    #'place' : _check_place,
    'report_type': _check_report_type,
    'thesis_type': _check_thesis_type,
    'extra_report_numbers': _check_extra_report_numbers,
    'isbn': _check_isbn,
    'issn': _check_issn,
    'supervisors': _check_supervisors,
    'university': _check_university,
}
"""
Dictionary of metadata field validator functions.
"""
