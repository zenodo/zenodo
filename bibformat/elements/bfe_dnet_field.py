# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2010, 2001 CERN.
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
"""BibFormat element - Prints a custom field
"""

from invenio.bibformat_utils import parse_tag
from invenio.dnetutils import load_vocabulary_from_file

def format_element(bfo, tag, vocabulary, instances_separator=" ",
           subfields_separator=" ", extension=""):
    """
    Prints the given field of a record.
    If tag is in range [001, 010], this element assumes
    that it accesses a control field. Else it considers it
    accesses a data field.

    @param tag: the tag code of the field that is to be printed
    @param instances_separator: a separator between instances of field
    @param subfields_separator: a separator between subfields of an instance
    @param vocabulary: the name of a D-NET vocabulary to use.
    """
    # Check if data or control field
    vocabulary = load_vocabulary_from_file(vocabulary)
    p_tag = parse_tag(tag)
    if p_tag[0].isdigit() and int(p_tag[0]) in range(0, 11):
        return  vocabulary.get(bfo.control_field(tag), "")
    elif p_tag[0].isdigit():
        # Get values without subcode.
        # We will filter unneeded subcode later
        if p_tag[1] == '':
            p_tag[1] = '_'
        if p_tag[2] == '':
            p_tag[2] = '_'
        values = bfo.fields(p_tag[0]+p_tag[1]+p_tag[2]) # Values will
                                                        # always be a
                                                        # list of
                                                        # dicts
    else:
        return ''

    x = 0
    instances_out = [] # Retain each instance output
    for instance in values:
        filtered_values = [value for (subcode, value) in instance.iteritems()
                          if p_tag[3] == '' or p_tag[3] == '%' \
                           or p_tag[3] == subcode]
        filtered_values = [vocabulary[value] for value in filtered_values if value in vocabulary]
        if len(filtered_values) > 0:
            instances_out.append(subfields_separator.join(filtered_values))

    return instances_separator.join(instances_out)
