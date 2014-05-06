# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
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

from invenio.modules.jsonalchemy.jsonext.functions.util_merge_fields_info_list \
    import util_merge_fields_info_list


def sync_authors(self, field_name, connected_field, action):  # pylint: disable=W0613
    """Sync authors content only when `__setitem__` or similar is used"""
    if action == 'set':
        if field_name == 'authors' and self.get('authors'):
            self.__setitem__('_first_author', self['authors'][0],
                             exclude=['connect'])
            if self['authors'][1:]:
                self.__setitem__('_additional_authors', self['authors'][1:],
                                 exclude=['connect'])
        elif field_name in ('_first_author', '_additional_authors'):
            self.__setitem__(
                'authors',
                util_merge_fields_info_list(self, ['_first_author',
                                            '_additional_authors']),
                exclude=['connect'])
