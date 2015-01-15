# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
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

"""Provide BibTeX formatter."""

import textwrap

import six
from slugify import slugify


class MissingRequiredFieldError(Exception):

    """Base class for exceptions in this module.

    The exception should be raised when the specific,
    required filed doesn't exist in the record.
    """

    def _init_(self, field):
        self.field = field

    def _str_(self):
        return "Missing filed: " + self.field


class Bibtex(object):

    """BibTeX formatter."""

    def __init__(self, record):
        """Initialize BibTEX formatter with the specific record."""
        self.record = record

    def format(self):
        """Return BibTeX export for single record."""
        formats = {
            'dataset': self._format_misc,
            'image': self._format_misc,
            'poster': self._format_misc,
            'presentation': self._format_misc,
            'publication': self._format_publication,
            'software': self._format_misc,
            'video': self._format_misc,
            'default': self._format_misc,
        }
        type = self._get_entry_type()
        if type in formats:
            return formats[type]()
        else:
            return formats['default']()

    def _format_publication(self):
        formats = {
            'book': [self._format_book,
                     self._format_booklet,
                     self._format_misc],
            'section': [self._format_inbook,
                        self._format_misc],
            'conferencepaper': [self._format_inproceedings,
                                self._format_proceedings,
                                self._format_misc],
            'article': [self._format_article,
                        self._format_misc],
            'patent': self._format_misc,
            'preprint': [self._format_unpublished,
                         self._format_misc],
            'report': [self._format_techreport,
                       self._format_misc],
            'thesis': [self._format_thesis,
                       self._format_misc],
            'technicalnote': [self._format_techreport,
                              self._format_manual,
                              self._format_misc],
            'workingpaper': [self._format_unpublished,
                             self._format_misc],
            'other': self._format_misc,
            'default': self._format_misc,
        }
        subtype = self._get_entry_subtype()
        if subtype in formats:
            for format in formats[subtype]:
                try:
                    out = format()
                except MissingRequiredFieldError:
                    continue
                else:
                    return out
        else:
            return formats['default']()

    def _format_entry(self, name, req, opt, ign):
        try:
            out = "@" + name + "{"
            out += self._get_citation_key() + ",\n"
            out += self._fetch_fields(req, opt, ign)
            out += "}"
            return out
        except MissingRequiredFieldError as e:
            raise e

    def _format_article(self):
        """Format article entry type.

        An article from a journal or magazine.
        """
        name = "article"
        req_fileds = ['author', 'title', 'journal', 'year']
        opt_fileds = ['volume', 'number', 'pages',
                      'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self._format_entry(name, req_fileds,
                                      opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_book(self):
        """Format book entry type.

        A book with an explicit publisher.
        """
        name = "book"
        req_fileds = ['author', 'title', 'publisher', 'year']
        # TODO: author or editor
        opt_fileds = ['volume', 'series', 'address', 'edition',
                      'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self._format_entry(name, req_fileds,
                                      opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_booklet(self):
        """Format article entry type.

        A work that is printed and bound, but without a named publisher
        or sponsoring institution.
        """
        name = "booklet"
        req_fileds = ['title']
        opt_fileds = ['author', 'howpublished', 'address',
                      'month', 'year', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self._format_entry(name, req_fileds,
                                      opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_inbook(self):
        """Format article entry type.

        A part of a book, which may be a chapter and/or a range of pages.
        """
        name = "conference"
        req_fileds = ['author', 'title', 'chapter', 'publisher', 'year']
        # TODO author or editor, chapter or pages
        opt_fileds = ['volume', 'series', 'address', 'edition',
                      'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self._format_entry(name, req_fileds,
                                      opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_proceedings(self):
        """Format article entry type.

        The proceedings of a conference.
        """
        name = "proceedings"
        req_fileds = ['title', 'year']
        opt_fileds = ['editor', 'publisher', 'organization',
                      'address', 'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self._format_entry(name, req_fileds,
                                      opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_inproceedings(self):
        """Format article entry type.

        An article in the proceedings of a conference.
        """
        name = "inproceedings"
        req_fileds = ['author', 'title', 'booktitle', 'year']
        opt_fileds = ['editor', 'pages', 'organization', 'publisher'
                      'address', 'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self._format_entry(name, req_fileds,
                                      opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_unpublished(self):
        """Format article entry type.

        A document with an author and title, but not formally published.
        """
        name = "unpublished"
        req_fileds = ['author', 'title', 'note']
        opt_fileds = ['month', 'year', 'key']
        ign_fields = ['doi', 'url']

        try:
            return self._format_entry(name, req_fileds,
                                      opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_techreport(self):
        """Format article entry type.

        A report published by a school or other institution, usually numbered
        within a series.
        """
        name = "techreport"
        req_fileds = ['author', 'title', 'institution', 'year']
        opt_fileds = ['type', 'number', 'address',
                      'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self._format_entry(name, req_fileds,
                                      opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_manual(self):
        """Format article entry type.

        Technical documentation.
        """
        name = "manual"
        req_fileds = ['title']
        opt_fileds = ['author', 'organization', 'address', 'edition',
                      'month', 'year', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self._format_entry(name, req_fileds,
                                      opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_thesis(self):
        """Format article entry type.

        An article from a journal or magazine.
        """
        name = "phdthesis"
        req_fileds = ['author', 'title', 'school', 'year']
        opt_fileds = ['address', 'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self._format_entry(name, req_fileds,
                                      opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_misc(self):
        """Format misc entry type.

        For use when nothing else fits.
        """
        name = "misc"
        req_fileds = []
        opt_fileds = ['author', 'title', 'month',
                      'year', 'note', 'howpublished', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self._format_entry(name, req_fileds,
                                      opt_fileds, ign_fields)
        except:
            return "This record cannot be exported to BibTEX."

    def _fetch_fields(self, req_fileds, opt_fileds=[], ign_fields=[]):
        fields = {
            'address': self._get_address,
            'annote': self._get_annote,
            'author': self._get_author,
            'booktitle': self._get_booktitle,
            'chapter': self._get_chapter,
            'crossref': self._get_crossref,
            'edition': self._get_edition,
            'editor': self._get_editor,
            'howpublished': self._get_howpublished,
            'institution': self._get_institution,
            'journal': self._get_journal,
            'key': self._get_key,
            'month': self._get_month,
            'note': self._get_note,
            'number': self._get_number,
            'organization': self._get_organization,
            'pages': self._get_pages,
            'publisher': self._get_publisher,
            'school': self._get_school,
            'series': self._get_series,
            'title': self._get_title,
            'type': self._get_type,
            'url': self._get_url,
            'volume': self._get_volume,
            'year': self._get_year,

            'doi': self._get_doi
        }
        out = ""
        for field in req_fileds:
            value = fields[field]()
            if value:
                out += self._format_output_row(field, value)
            else:
                raise MissingRequiredFieldError(field)
        for field in opt_fileds:
            value = fields[field]()
            if value:
                out += self._format_output_row(field, value)
        for field in ign_fields:
            value = fields[field]()
            if value:
                out += self._format_output_row(field, value)
        return out

    def _format_output_row(self, field, value):
        out = ""  # FIXME handle all fields
        if field == "author":
            if len(value) == 1:
                out += u"  {0:<12} = {{{1}}}\n".format(field, value[0])
            else:
                out += u"  {0:<12} = {{{1} and\n".format(field, value[0])
            if len(value) > 1:
                for line in value[1:-1]:
                    out += u" {0:<16} {1:<} and\n".format("", line)
                out += u" {0:<16} {1:<}}},\n".format("", value[-1])
        elif len(value) >= 50:
            wrapped = textwrap.wrap(value, 50)
            out += u"  {0:<12} = {{{{{1} \n".format(field, wrapped[0])
            for line in wrapped[1:-1]:
                out += u" {0:<17} {1:<}\n".format("", line)
            out += u" {0:<17} {1:<}}}}},\n".format("", wrapped[-1])
        elif field == "month":
            out += u"  {0:<12} = {1},\n".format(field, value)
        elif field == "url":
            out += u"  {0:<12} = {{{1}}}\n".format(field, value)
        else:
            if(self._is_number(value)):
                out += u"  {0:<12} = {1},\n".format(field, value)
            else:
                out += u"  {0:<12} = {{{1}}},\n".format(field, value)
        return out

    def _is_number(self, s):
        try:
            int(s)
            return True
        except (ValueError, TypeError):
            return False

    def _get_entry_type(self):
        """Return entry type."""
        if 'upload_type' in self.record:
            if 'type' in self.record['upload_type']:
                return self.record['upload_type']['type']
        return 'default'

    def _get_entry_subtype(self):
        """Return entry subtype."""
        if 'upload_type' in self.record:
            if 'subtype' in self.record['upload_type']:
                return self.record['upload_type']['subtype']
        return 'default'

    def _get_citation_key(self):
        """Return citation key."""
        if "recid" in self.record:
            first_author = self.record.get("first_author", None)
            if first_author:
                name = first_author.get(
                    "familyname",
                    first_author.get("name")
                )
                pubdate = self.record.get('publication_date', None)
                if pubdate:
                    year = "{}_{}".format(pubdate.year, self.record["recid"])
                else:
                    year = self.record["recid"]

                return "{0}_{1}".format(slugify(
                    name,
                    to_lower=True,
                    separator="_",
                    max_length=40,
                    ),
                    year
                )
            else:
                return six.text_type(self.record["recid"])
        else:
            raise MissingRequiredFieldError("citation key")

    def _get_doi(self):
        """Return doi."""
        if "doi" in self.record:
            return self.record['doi']
        else:
            raise MissingRequiredFieldError("doi")

    def _get_author(self):
        """Return list of name(s) of the author(s)."""
        result = []
        if "authors" in self.record:
            for author in self.record['authors']:
                result.append(author["name"])
            return result
        else:
            return result

    def _get_title(self):
        """Return work's title."""
        if "title" in self.record:
            return self.record['title'].strip()
        else:
            return ""

    def _get_month(self):
        """Return the month in which the work was published."""
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        if "publication_date" in self.record:
            return months[self.record["publication_date"].month - 1]
        else:
            return ""

    def _get_year(self):
        """Return the year of publication."""
        if "publication_date" in self.record:
            return self.record["publication_date"].strftime("%Y")
        else:
            return ""

    def _get_note(self):
        """Return any additional information that can help the reader."""
        if "notes" in self.record:
            return self.record["notes"]
        else:
            return ""

    def _get_address(self):
        """Return publisher's address."""
        if "imprint" in self.record and\
                "place" in self.record["imprint"]:
            return self.record["imprint"]["place"]
        else:
            return ""

    def _get_annote(self):
        """Return an annotation for annotated bibliography styles.

        NOTE: unsupported
        """
        return ""

    def _get_booktitle(self):
        """Return the title of the book, part of which is being cited."""
        if "part_of" in self.record and\
                "title" in self.record["part_of"]:
            return self.record["part_of"]["title"]
        else:
            return ""

    def _get_chapter(self):
        """Return the chapter number.

        NOTE: unsupported
        """
        return ""

    def _get_crossref(self):
        """Return the key of the cross-referenced entry.

        NOTE: unsupported
        """
        return ""

    def _get_edition(self):
        """Return the edition of a book, long form.

        NOTE: unsupported
        """
        return ""

    def _get_editor(self):
        """Return the name(s) of the editor(s).

        NOTE: unsupported
        """
        return ""

    def _get_howpublished(self):
        """Return information on how the record was published.

        NOTE: unsupported
        """
        return ""

    def _get_institution(self):
        """Return the institution that was involved in the publishing.

        NOTE: unsupported
        """
        return ""

    def _get_journal(self):
        """Return the journal or magazine the work was published in."""
        if "journal" in self.record and\
                "title" in self.record["journal"]:
            return self.record["journal"]["title"]
        else:
            return ""

    def _get_key(self):
        """Return record's hidden field.

        Used for specifying or overriding
        the alphabetical order of entries (when the "author" and "editor"
        fields are missing). Note that this is very different from the key
        (mentioned just after this list) that is used to cite or
        cross-reference the entry.

        NOTE: unsupported
        """
        return ""

    def _get_number(self):
        """Return the (issue) number of a journal, magazine, or tech-report."""
        if "journal" in self.record and\
                "issue" in self.record["journal"]:
            return self.record["journal"]["issue"]
        else:
            return ""

    def _get_organization(self):
        """Return the conference sponsor.

        NOTE: unsupported
        """
        return ""

    def _get_pages(self):
        """Return page numbers, separated by commas or double-hyphens."""
        if "journal" in self.record and\
                "pages" in self.record["journal"]:
            return self.record["journal"]["pages"]
        elif "part_of" in self.record and\
                "pages" in self.record["part_of"]:
            return self.record["part_of"]["pages"]
        else:
            return ""

    def _get_publisher(self):
        """Return the publisher's name."""
        if "imprint" in self.record and\
                "publisher" in self.record["imprint"]:
            return self.record["imprint"]["publisher"]
        elif "part_of" in self.record and\
                "publisher" in self.record["part_of"]:
            return self.record["part_of"]["publisher"]
        else:
            from invenio.base.globals import cfg
            return cfg.get("CFG_SITE_NAME", "")

    def _get_school(self):
        """Return the school where the thesis was written."""
        if "thesis_university" in self.record:
            return self.record["thesis_university"]
        else:
            return ""

    def _get_series(self):
        """Return the series of books the book was published in.

        NOTE: unsupported
        """
        return ""

    def _get_type(self):
        """Return the field overriding the default type of publication.

        NOTE: unsupported
        """
        return ""

    def _get_url(self):
        """Return the WWW address."""
        if "doi" in self.record:
            doi = self.record['doi']
            return "http://dx.doi.org/%s" % doi
        else:
            return ""

    def _get_volume(self):
        """Return the volume of a journal or multi-volume book."""
        if "journal" in self.record and \
                "volume" in self.record["journal"]:
            return self.record["journal"]["volume"]
        else:
            return ""
