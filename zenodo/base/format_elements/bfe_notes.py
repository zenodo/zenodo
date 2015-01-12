# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2012, 2013 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.


"""BibFormat element - Prints notes
"""
__revision__ = "$Id$"

import cgi

def format_element(bfo, note_suffix, note_prefix='Note: ', separator='; '):
    """
    Displays notes (various note fields)

    @param note_prefix: a prefix before each group of notes
    @param note_suffix: a suffix after each group of notes
    @param separator: a separator between notes of a group
    """
    notes = []

    notes_group_1 = bfo.fields('594__p')
    if len(notes_group_1) > 0:
        notes_group_1 = separator.join(notes_group_1)
        notes.append(notes_group_1)

    notes_group_2 = bfo.fields('500__a')
    if len(notes_group_2) > 0:
        notes_group_2 = separator.join(notes_group_2)
        notes.append(notes_group_2)


    notes_group_3 = bfo.fields('502__a')
    notes_group_3.extend(bfo.fields('909CCr'))
    notes_group_3.extend(bfo.fields('909CPn'))
    # OPENAIRE: Don't use 711 where conference information is stored
    #notes_group_3.extend(bfo.fields('711__a'))
    if len(notes_group_3) > 0:
        notes_group_3 = separator.join(notes_group_3)
        notes.append(notes_group_3)

    notes_group_4 = bfo.fields('596__a')

    if len(notes_group_4) > 0:
        notes_group_4 = separator.join(notes_group_4)
        notes.append(notes_group_4)

    if len(notes) > 0:

        notes  = [note_prefix + cgi.escape(x) + note_suffix
                  for x in notes]
        return "".join(notes)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
