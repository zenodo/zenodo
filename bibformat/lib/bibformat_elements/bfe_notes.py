# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011 CERN.
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
