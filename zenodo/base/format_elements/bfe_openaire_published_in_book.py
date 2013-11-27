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


def format_element(bfo):
    """
    Generate a line similar to below (used for chapters to include the book
    they are part of):

    Book title. Place: Publisher (Year). pages. ISBN: XXXXX
    """
    book = filter(lambda x: 'bookpart' == x.get('n', ''), bfo.fields('773__'))

    if len(book) != 1:
        return ""
    book = book[0]

    place = book.get('a', '')
    publisher = book.get('b', '')
    pages = book.get('g', '')
    title = book.get('t', '')
    year = book.get('c', '')
    isbn = book.get('z', '')

    ret = ["%(title)s"]

    if place and publisher:
        ret.append("%(place)s: %(publisher)s (%(year)s)")
    elif place:
        ret.append("%(place)s (%(year)s)")
    elif publisher:
        ret.append("%(publisher)s (%(year)s)")

    if pages:
        ret.append("%(pages)s")

    if isbn:
        ret.append("ISBN: %(isbn)s")

    ret = ". ".join(ret)

    return ret % {
        'title': title,
        'publisher': publisher,
        'pages': pages,
        'place': place,
        'isbn': isbn,
        'year': year,
    }


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 1
