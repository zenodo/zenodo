# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


"""BibFormat element - Prints subjects"""


__revision__ = "$Id$"

import cgi
from urllib import quote
from invenio.config import CFG_BASE_URL


def format_element(bfo, subjects_prefix, subjects_suffix, separator=' ; ',
                   link='yes'):
    """
    Display subjects of the record.

    @param subject_prefix: a prefix before each subject
    @param subject_suffix: a suffix after each subject
    @param separator: a separator between subjects
    @param link: links the subjects if 'yes' (HTML links)
    """
    subjects = bfo.fields('6501_a')

    if len(subjects) > 0:
        if link == 'yes':
            subjects = ['<a href="' + CFG_BASE_URL +
                        '/search?f=keyword&amp;p=' +
                        quote('"' + subject + '"') +
                        '&amp;ln=' + str(bfo.lang) +
                        '">' + cgi.escape(subject) + '</a>'
                        for subject in subjects]
        else:
            subjects = [cgi.escape(subject)
                        for subject in subjects]

        subjects = [subjects_prefix + subject + subjects_suffix
                    for subject in subjects]
        return separator.join(subjects)


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
