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


def get_files_from_bibdoc(recid):
    """ Retrieve all the files related with a given record.

    @param recid

    @return List of dictionaries containing all the information stored
            inside BibDoc if the current record has files attached, the
            empty list otherwise
    """
    if not recid or recid < 0:
        return []

    from invenio.legacy.bibdocfile.api import BibRecDocs, \
        InvenioBibDocFileError
    files = []
    try:
        bibrecdocs = BibRecDocs(int(recid))
    except InvenioBibDocFileError:
        return []
    latest_files = bibrecdocs.list_latest_files()
    for afile in latest_files:
        file_dict = {}
        file_dict['comment'] = afile.get_comment()
        file_dict['description'] = afile.get_description()
        file_dict['eformat'] = afile.get_format()
        file_dict['full_name'] = afile.get_full_name()
        file_dict['full_path'] = afile.get_full_path()
        file_dict['magic'] = afile.get_magic()
        file_dict['name'] = afile.get_name()
        file_dict['path'] = afile.get_path()
        file_dict['size'] = afile.get_size()
        file_dict['status'] = afile.get_status()
        file_dict['subformat'] = afile.get_subformat()
        file_dict['superformat'] = afile.get_superformat()
        file_dict['type'] = afile.get_type()
        file_dict['url'] = afile.get_url()
        file_dict['version'] = afile.get_version()
        files.append(file_dict)
    return files
