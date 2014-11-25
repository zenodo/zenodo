# -*- coding: utf-8 -*-
##
## This file is part of ZENODO.
## Copyright (C) 2012, 2013, 2014 CERN.
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

"""Provide BibTeX formatter."""

import textwrap

from invenio.base.globals import cfg


class Bibtex(object):

    """BibTeX formatter."""

    def __init__(self, record):
        """Initialize BibTEX formatter with the specific record."""
        self.record = record

    def format(self):
        """Return BibTeX export for single record."""
        formats = {
            'dataset': self.__format_misc,
            'image': self.__format_misc,
            'poster': self.__format_misc,
            'presentation': self.__format_misc,
            'publication': self.__format_publication,
            'software': self.__format_misc,
            'video': self.__format_misc,
            'default': self.__format_misc,
        }
        type = self.__get_entry_type()
        if type in formats:
            return formats[type]()
        else:
            return formats['default']()

    def __format_publication(self):
        """Function description."""
        formats = {
            'book': [self.__format_book,
                     self.__format_booklet,
                     self.__format_misc],
            'section': [self.__format_inbook,
                        self.__format_misc],
            'conferencepaper': [self.__format_inproceedings,
                                self.__format_proceedings,
                                self.__format_misc],
            'article': [self.__format_article,
                        self.__format_misc],
            'patent': self.__format_misc,
            'preprint': [self.__format_unpublished,
                         self.__format_misc],
            'report': [self.__format_techreport,
                       self.__format_misc],
            'thesis': [self.__format_thesis,
                       self.__format_misc],
            'technicalnote': [self.__format_techreport,
                              self.__format_manual,
                              self.__format_misc],
            'workingpaper': [self.__format_unpublished,
                             self.__format_misc],
            'other': self.__format_misc,
            'default': self.__format_misc,
        }
        subtype = self.__get_entry_subtype()
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

    def __format_entry(self, name, req, opt, ign):
        try:
            out = "@"+name+"{"
            out += self.__get_citation_key() + ",\n"
            out += self.__fetch_fields(req, opt, ign)
            out += "}"
            return out
        except MissingRequiredFieldError as e:
            raise e

    def __format_article(self):
        """Format article entry type:
           An article from a journal or magazine."""
        name = "article"
        req_fileds = ['author', 'title', 'journal', 'year']
        opt_fileds = ['volume', 'number', 'pages',
                      'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self.__format_entry(name, req_fileds,
                                       opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def __format_book(self):
        """Format book entry type:
           A book with an explicit publisher."""
        name = "book"
        req_fileds = ['author', 'title', 'publisher', 'year']
        #TODO: author or editor
        opt_fileds = ['volume', 'series', 'address', 'edition',
                      'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self.__format_entry(name, req_fileds,
                                       opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def __format_booklet(self):
        """Format article entry type:
           A work that is printed and bound, but without a named publisher
           or sponsoring institution."""
        name = "booklet"
        req_fileds = ['title']
        opt_fileds = ['author', 'howpublished', 'address',
                      'month', 'year', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self.__format_entry(name, req_fileds,
                                       opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def __format_inbook(self):
        """Format article entry type:
           A part of a book, which may be a chapter and/or a range of pages."""
        name = "conference"
        req_fileds = ['author', 'title', 'chapter', 'publisher', 'year']
        #TODO author or editor, chapter or pages
        opt_fileds = ['volume', 'series', 'address', 'edition',
                      'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self.__format_entry(name, req_fileds,
                                       opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def __format_proceedings(self):
        """Format article entry type:
           The proceedings of a conference."""
        name = "proceedings"
        req_fileds = ['title', 'year']
        opt_fileds = ['editor', 'publisher', 'organization',
                      'address', 'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self.__format_entry(name, req_fileds,
                                       opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def __format_inproceedings(self):
        """Format article entry type:
           An article in the proceedings of a conference"""
        name = "inproceedings"
        req_fileds = ['author', 'title', 'booktitle', 'year']
        opt_fileds = ['editor', 'pages', 'organization', 'publisher'
                      'address', 'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self.__format_entry(name, req_fileds,
                                       opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def __format_unpublished(self):
        """Format article entry type:
           A document with an author and title, but not formally published."""
        name = "unpublished"
        req_fileds = ['author', 'title', 'note']
        opt_fileds = ['month', 'year', 'key']
        ign_fields = ['doi', 'url']

        try:
            return self.__format_entry(name, req_fileds,
                                       opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def __format_techreport(self):
        """Format article entry type:
           A report published by a school or other institution,
           usually numbered within a series."""
        name = "techreport"
        req_fileds = ['author', 'title', 'institution', 'year']
        opt_fileds = ['type', 'number', 'address',
                      'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self.__format_entry(name, req_fileds,
                                       opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def __format_manual(self):
        """Format article entry type:
           Technical documentation."""
        name = "manual"
        req_fileds = ['title']
        opt_fileds = ['author', 'organization', 'address', 'edition',
                      'month', 'year', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self.__format_entry(name, req_fileds,
                                       opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def __format_thesis(self):
        """Format article entry type:
           An article from a journal or magazine."""
        name = "phdthesis"
        req_fileds = ['author', 'title', 'school', 'year']
        opt_fileds = ['address', 'month', 'note', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self.__format_entry(name, req_fileds,
                                       opt_fileds, ign_fields)
        except MissingRequiredFieldError as e:
            raise e

    def __format_misc(self):
        """Format misc entry type:
           For use when nothing else fits."""
        name = "misc"
        req_fileds = []
        opt_fileds = ['author', 'title', 'month',
                      'year', 'note', 'howpublished', 'key']
        ign_fields = ['doi', 'url']
        try:
            return self.__format_entry(name, req_fileds,
                                       opt_fileds, ign_fields)
        except:
            return "This record cannot be exported to BibTEX."

    def __fetch_fields(self, req_fileds, opt_fileds=[], ign_fields=[]):
        """Function description."""
        fields = {
            'address': self.__get_address,
            'annote': self.__get_annote,
            'author': self.__get_author,
            'booktitle': self.__get_booktitle,
            'chapter': self.__get_chapter,
            'crossref': self.__get_crossref,
            'edition': self.__get_edition,
            'editor': self.__get_editor,
            'howpublished': self.__get_howpublished,
            'institution': self.__get_institution,
            'journal': self.__get_journal,
            'key': self.__get_key,
            'month': self.__get_month,
            'note': self.__get_note,
            'number': self.__get_number,
            'organization': self.__get_organization,
            'pages': self.__get_pages,
            'publisher': self.__get_publisher,
            'school': self.__get_school,
            'series': self.__get_series,
            'title': self.__get_title,
            'type': self.__get_type,
            'url': self.__get_url,
            'volume': self.__get_volume,
            'year': self.__get_year,

            'doi': self.__get_doi
        }
        out = ""
        for field in req_fileds:
            value = fields[field]()
            if value:
                out += self.__format_output_row(field, value)
            else:
                raise MissingRequiredFieldError(field)
        for field in opt_fileds:
            value = fields[field]()
            if value:
                out += self.__format_output_row(field, value)
        for field in ign_fields:
            value = fields[field]()
            if value:
                out += self.__format_output_row(field, value)
        return out

    def __format_output_row(self, field, value):
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
            if(self.__is_number(value)):
                out += u"  {0:<12} = {1},\n".format(field, value)
            else:
                out += u"  {0:<12} = {{{1}}},\n".format(field, value)
        return out

    def __is_number(self, s):
        try:
            int(s)
            return True
        except (ValueError, TypeError):
            return False

    def __get_entry_type(self):
        """Return entry type."""
        if 'upload_type' in self.record:
            if 'type' in self.record['upload_type']:
                return self.record['upload_type']['type']
        return 'default'

    def __get_entry_subtype(self):
        """Return entry subtype."""
        if 'upload_type' in self.record:
            if 'subtype' in self.record['upload_type']:
                return self.record['upload_type']['subtype']
        return 'default'

    def __get_citation_key(self):
        """Return citation key."""
        if "_id" in self.record:  # FIXME only way ?
            if "_first_author" in self.record and \
               "familyname" in self.record["_first_author"] and \
               " " not in self.record["_first_author"]["familyname"]:
                return self.record["_first_author"]["familyname"] +\
                    ":" + str(self.record["_id"])
            else:
                return str(self.record["_id"])
        else:
            raise MissingRequiredFieldError("citation key")

    def __get_doi(self):
        """Return doi."""
        if "doi" in self.record:
            return self.record['doi']
        else:
            raise MissingRequiredFieldError("doi")

    def __get_author(self):
        """Return list of name(s) of the author(s)."""
        result = []
        if "authors" in self.record:
            for author in self.record['authors']:
                result.append(author["name"])
            return result
        else:
            return result

    def __get_title(self):
        """Return work's title."""
        if "title" in self.record:
            return self.record['title'].strip()
        else:
            return ""

    def __get_month(self):
        """Return the month in which the work was published
        (or, if unpublished, the month of creation)."""
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        if "publication_date" in self.record:
            return months[self.record["publication_date"].month-1]
        else:
            return ""

    def __get_year(self):
        """Return the year of publication
        (or, if unpublished, the year of creation)."""
        if "publication_date" in self.record:
            return self.record["publication_date"].strftime("%Y")
        else:
            return ""

    def __get_note(self):
        """Return any additional information that can help the reader."""
        if "notes" in self.record:
            return self.record["notes"]
        else:
            return ""

    def __get_address(self):
        """Return publisher's (or other institution's) address
        (usually just the city, but can be the full address
         for lesser-known publishers)."""
        if "imprint" in self.record and\
                "place" in self.record["imprint"]:
            return self.record["imprint"]["place"]
        else:
            return ""

    def __get_annote(self):
        """Return an annotation for annotated bibliography
        styles (not typical).

        NOTE: unsupported"""
        return ""

    def __get_booktitle(self):
        """Return the title of the book, part of which is being cited."""
        if "part_of" in self.record and\
                "title" in self.record["part_of"]:
            return self.record["part_of"]["title"]
        else:
            return ""

    def __get_chapter(self):
        """Return the chapter number.

        NOTE: unsupported"""
        return ""

    def __get_crossref(self):
        """Return the key of the cross-referenced entry.

        NOTE: unsupported"""
        return ""

    def __get_edition(self):
        """Return the edition of a book, long form (such as
        "First" or "Second").

        NOTE: unsupported"""
        return ""

    def __get_editor(self):
        """Return the name(s) of the editor(s).

        NOTE: unsupported"""
        return ""

    def __get_howpublished(self):
        """Return information on how the record was published,
        if the publishing method is nonstandard.

        NOTE: unsupported"""
        return ""

    def __get_institution(self):
        """Return the institution that was involved in the publishing,
        but not necessarily the publisher.

        NOTE: unsupported"""
        return ""

    def __get_journal(self):
        """Return the journal or magazine the work was published in."""
        if "journal" in self.record and\
                "title" in self.record["journal"]:
            return self.record["journal"]["title"]
        else:
            return ""

    def __get_key(self):
        """Return record's hidden field used for specifying or overriding
        the alphabetical order of entries (when the "author" and "editor"
        fields are missing). Note that this is very different from the key
        (mentioned just after this list) that is used to cite or
        cross-reference the entry.

        NOTE: unsupported"""
        return ""

    def __get_number(self):
        """Return the "(issue) number" of a journal, magazine, or tech-report,
        if applicable. (Most publications have a "volume", but no "number")."""
        if "journal" in self.record and\
                "issue" in self.record["journal"]:
            return self.record["journal"]["issue"]
        else:
            return ""

    def __get_organization(self):
        """Return the conference sponsor.

        NOTE: unsupported"""
        return ""

    def __get_pages(self):
        """Return page numbers, separated by commas or double-hyphens."""
        if "journal" in self.record and\
                "pages" in self.record["journal"]:
            return self.record["journal"]["pages"]
        elif "part_of" in self.record and\
                "pages" in self.record["part_of"]:
            return self.record["part_of"]["pages"]
        else:
            return ""

    def __get_publisher(self):
        """Return the publisher's name."""
        if "imprint" in self.record and\
                "publisher" in self.record["imprint"]:
            return self.record["imprint"]["publisher"]
        elif "part_of" in self.record and\
                "publisher" in self.record["part_of"]:
            return self.record["part_of"]["publisher"]
        elif "CFG_SITE_NAME" in cfg:
            return cfg["CFG_SITE_NAME"]
        else:
            return ""

    def __get_school(self):
        """Return the school where the thesis was written."""
        if "thesis_university" in self.record:
            return self.record["thesis_university"]
        else:
            return ""

    def __get_series(self):
        """Return the series of books the book was published in
        (e.g. "Lecture Notes in Computer Science").

        NOTE: unsupported"""
        return ""

    def __get_type(self):
        """Return the field overriding the default type of publication
        (e.g. "Research Note" for techreport, "{PhD} dissertation"
        for phdthesis, "Section" for inbook/incollection).

        NOTE: unsupported"""
        return ""

    def __get_url(self):
        """Return the WWW address."""
        if "doi" in self.record:
            doi = self.record['doi']
            return "http://dx.doi.org/%s" % doi
        else:
            return ""

    def __get_volume(self):
        """Return the volume of a journal or multi-volume book."""
        if "journal" in self.record and\
                "volume" in self.record["journal"]:
            return self.record["journal"]["volume"]
        else:
            return ""


class MissingRequiredFieldError(Exception):
    """Base class for exceptions in this module.

    The exception should be raised when the specific,
    required filed doesn't exist in the record.

    Args:
        filed (str): Name of the field, which is missing.

    """

    def __init__(self, field):
        self.field = field

    def __str__(self):
        return "Missing filed: " + self.field
