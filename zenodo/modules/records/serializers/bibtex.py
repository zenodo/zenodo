# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
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

"""BibTeX serializer for records."""

from __future__ import absolute_import, print_function

import textwrap

import six
from dateutil.parser import parse as iso2dt
from flask import current_app
from slugify import slugify


class BibTeXSerializer(object):
    """BibTeX serializer for records."""

    # pylint: disable=W0613
    def serialize(self, pid, record, links_factory=None):
        """Serialize a single record and persistent identifier.

        :param pid: Persistent identifier instance.
        :param record: Record instance.
        :param links_factory: Factory function for record links.
        """
        return Bibtex(record=record).format()

    # pylint: disable=W0613
    def serialize_search(self, pid_fetcher, search_result, links=None,
                         item_links_factory=None):
        """Serialize a search result.

        :param pid_fetcher: Persistent identifier fetcher.
        :param search_result: Elasticsearch search result.
        :param links: Dictionary of links to add to response.
        """
        records = []
        for hit in search_result['hits']['hits']:
            records.append(Bibtex(record=hit['_source']).format())

        return "\n".join(records)


class MissingRequiredFieldError(Exception):
    """Base class for exceptions in this module.

    The exception should be raised when the specific,
    required field doesn't exist in the record.
    """

    def _init_(self, field):
        self.field = field

    def _str_(self):
        return "Missing field: " + self.field


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
        t = self._get_entry_type()
        if t in formats:
            return formats[t]()
        else:
            return formats['default']()

    def _format_publication(self):
        formats = {
            'book': [self._format_book,
                     self._format_booklet,
                     self._format_misc],
            'section': [self._format_misc],
            'conferencepaper': [self._format_inproceedings,
                                self._format_proceedings,
                                self._format_misc],
            'article': [self._format_article,
                        self._format_misc],
            'patent': self._format_misc,
            'preprint': [self._format_unpublished,
                         self._format_misc],
            'report': [self._format_misc],
            'thesis': [self._format_thesis,
                       self._format_misc],
            'technicalnote': [self._format_manual,
                              self._format_misc],
            'workingpaper': [self._format_unpublished,
                             self._format_misc],
            'other': [self._format_misc],
            'default': self._format_misc,
        }
        subtype = self._get_entry_subtype()
        if subtype in formats:
            for f in formats[subtype]:
                try:
                    out = f()
                except MissingRequiredFieldError:
                    continue
                else:
                    return out
        else:
            return formats['default']()

    def _format_entry(self, name, req, opt, ign):
        out = "@" + name + "{"
        out += self._get_citation_key() + ",\n"
        out += self._clean_input(self._fetch_fields(req, opt, ign))
        out += "}"
        return out

    def _clean_input(self,input):
        unsupported_char = ['&']
        chars = list(input)
        for index, char in enumerate(chars):
            if char in unsupported_char:
                chars[index] = "\\" + chars[index]
        return ''.join(chars)

    def _format_article(self):
        """Format article entry type.

        An article from a journal or magazine.
        """
        name = "article"
        req_fields = ['author', 'title', 'journal', 'year']
        opt_fields = ['volume', 'number', 'pages', 'month', 'note']
        ign_fields = ['doi', 'url']
        return self._format_entry(name, req_fields,
                                  opt_fields, ign_fields)

    def _format_book(self):
        """Format book entry type.

        A book with an explicit publisher.
        """
        name = "book"
        req_fields = ['author', 'title', 'publisher', 'year']
        opt_fields = ['volume', 'address', 'month', 'note']
        ign_fields = ['doi', 'url']
        return self._format_entry(name, req_fields,
                                  opt_fields, ign_fields)

    def _format_booklet(self):
        """Format article entry type.

        A work that is printed and bound, but without a named publisher
        or sponsoring institution.
        """
        name = "booklet"
        req_fields = ['title']
        opt_fields = ['author', 'address', 'month', 'year', 'note']
        ign_fields = ['doi', 'url']
        return self._format_entry(name, req_fields,
                                  opt_fields, ign_fields)

    def _format_proceedings(self):
        """Format article entry type.

        The proceedings of a conference.
        """
        name = "proceedings"
        req_fields = ['title', 'year']
        opt_fields = ['publisher', 'address', 'month', 'note']
        ign_fields = ['doi', 'url']
        return self._format_entry(name, req_fields,
                                  opt_fields, ign_fields)

    def _format_inproceedings(self):
        """Format article entry type.

        An article in the proceedings of a conference.
        """
        name = "inproceedings"
        req_fields = ['author', 'title', 'booktitle', 'year']
        opt_fields = ['pages', 'publisher', 'address', 'month', 'note', 'venue']
        ign_fields = ['doi', 'url']
        return self._format_entry(name, req_fields,
                                  opt_fields, ign_fields)

    def _format_unpublished(self):
        """Format article entry type.

        A document with an author and title, but not formally published.
        """
        name = "unpublished"
        req_fields = ['author', 'title', 'note']
        opt_fields = ['month', 'year']
        ign_fields = ['doi', 'url']

        return self._format_entry(name, req_fields,
                                  opt_fields, ign_fields)

    def _format_manual(self):
        """Format article entry type.

        Technical documentation.
        """
        name = "manual"
        req_fields = ['title']
        opt_fields = ['author', 'address', 'month', 'year', 'note']
        ign_fields = ['doi', 'url']
        return self._format_entry(name, req_fields,
                                  opt_fields, ign_fields)

    def _format_thesis(self):
        """Format article entry type.

        An article from a journal or magazine.
        """
        name = "phdthesis"
        req_fields = ['author', 'title', 'school', 'year']
        opt_fields = ['address', 'month', 'note']
        ign_fields = ['doi', 'url']
        return self._format_entry(name, req_fields,
                                  opt_fields, ign_fields)

    def _format_misc(self):
        """Format misc entry type.

        For use when nothing else fits.
        """
        name = "misc"
        req_fields = []
        opt_fields = ['author', 'title', 'month', 'year', 'note']
        ign_fields = ['doi', 'url']
        return self._format_entry(name, req_fields,
                                  opt_fields, ign_fields)

    def _fetch_fields(self, req_fields, opt_fields=None, ign_fields=None):
        opt_fields = opt_fields or []
        ign_fields = ign_fields or []
        fields = {
            'address': self._get_address,
            'author': self._get_author,
            'booktitle': self._get_booktitle,
            'journal': self._get_journal,
            'month': self._get_month,
            'note': self._get_note,
            'number': self._get_number,
            'pages': self._get_pages,
            'publisher': self._get_publisher,
            'school': self._get_school,
            'title': self._get_title,
            'url': self._get_url,
            'venue': self._get_venue,
            'volume': self._get_volume,
            'year': self._get_year,
            'doi': self._get_doi
        }
        out = ""
        for field in req_fields:
            value = fields[field]()
            if value:
                out += self._format_output_row(field, value)
            else:
                raise MissingRequiredFieldError(field)
        for field in opt_fields:
            value = fields[field]()
            if value:
                out += self._format_output_row(field, value)
        for field in ign_fields:
            value = fields[field]()
            if value:
                out += self._format_output_row(field, value)
        return out

    def _format_output_row(self, field, value):
        out = ""
        if field == "author":
            if len(value) == 1:
                out += u"  {0:<12} = {{{1}}},\n".format(field, value[0])
            else:
                out += u"  {0:<12} = {{{1} and\n".format(field, value[0])
            if len(value) > 1:
                for line in value[1:-1]:
                    out += u" {0:<16} {1:<} and\n".format("", line)
                out += u" {0:<16} {1:<}}},\n".format("", value[-1])
        elif len(value) >= 50:
            if isinstance(value, six.string_types):
                value = value.strip()
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
        if 'resource_type' in self.record:
            if 'type' in self.record['resource_type']:
                return self.record['resource_type']['type']
        return 'default'

    def _get_entry_subtype(self):
        """Return entry subtype."""
        if 'resource_type' in self.record:
            if 'subtype' in self.record['resource_type']:
                return self.record['resource_type']['subtype']
        return 'default'

    def _get_citation_key(self):
        """Return citation key."""
        if "recid" in self.record:
            authors = self.record.get("creators", None)
            if authors:
                first_author = authors[0]
                name = first_author.get(
                    "familyname",
                    first_author.get("name")
                )
                pubdate = self.record.get('publication_date', None)
                if pubdate:
                    year = "{}_{}".format(iso2dt(pubdate).year,
                                          self.record['recid'])
                else:
                    year = self.record['recid']

                return "{0}_{1}".format(slugify(name, separator="_",
                                                max_length=40),
                                        year)
            else:
                return six.text_type(self.record['recid'])
        else:
            raise MissingRequiredFieldError("citation key")

    def _get_doi(self):
        """Return doi."""
        if "doi" in self.record:
            return self.record['doi']
        else:
            return None

    def _get_author(self):
        """Return list of name(s) of the author(s)."""
        result = []
        if "creators" in self.record:
            for author in self.record['creators']:
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
            return months[iso2dt(self.record["publication_date"]).month - 1]
        else:
            return ""

    def _get_year(self):
        """Return the year of publication."""
        if "publication_date" in self.record:
            return six.text_type(iso2dt(self.record["publication_date"]).year)
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

    def _get_booktitle(self):
        """Return the title of the book, part of which is being cited."""
        if "part_of" in self.record and\
                "title" in self.record["part_of"]:
            return self.record["part_of"]["title"]
        else:
            return ""

    def _get_journal(self):
        """Return the journal or magazine the work was published in."""
        if "journal" in self.record and\
                "title" in self.record["journal"]:
            return self.record["journal"]["title"]
        else:
            return ""

    def _get_number(self):
        """Return the (issue) number of a journal, magazine, or tech-report."""
        if "journal" in self.record and\
                "issue" in self.record["journal"]:
            return self.record["journal"]["issue"]
        else:
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
            return current_app.config.get("THEME_SITENAME", "")

    def _get_school(self):
        """Return the school where the thesis was written."""
        return self.record.get("thesis", {}).get("university", "")

    def _get_url(self):
        """Return the WWW address."""
        return "https://doi.org/%s" % self.record['doi'] \
            if "doi" in self.record else ""

    def _get_venue(self):
        """Return conference's venue."""
        if "meeting" in self.record and\
                "place" in self.record["meeting"]:
            return self.record["meeting"]["place"]
        else:
            return ""

    def _get_volume(self):
        """Return the volume of a journal or multi-volume book."""
        return self.record.get("journal", {}).get("volume", "")
