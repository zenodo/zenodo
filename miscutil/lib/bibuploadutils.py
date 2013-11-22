## This file is part of Invenio.
## Copyright (C) 2010, 2011, 2012 CERN.
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

import os
import uuid
from tempfile import mkstemp

from invenio.bibrecord import record_xml_output
from invenio.bibtask import task_low_level_submission
from invenio.config import CFG_TMPSHAREDDIR


CFG_MAX_RECORDS = 100


def open_temp_file(prefix):
    """
    Create a temporary file to write MARC XML in
    """
    # Prepare to save results in a tmp file
    (fd, filename) = mkstemp(
        dir=CFG_TMPSHAREDDIR,
        prefix=prefix + str(uuid.uuid4()),
        suffix='.xml'
    )
    file_out = os.fdopen(fd, "w")
    return (file_out, filename)


def close_temp_file(file_out, filename):
    """ Close temporary file again """
    file_out.close()
    os.chmod(filename, 0644)


def bibupload_record(record=None, collection=None,
                     file_prefix="bibuploadutils", mode="-c",
                     alias='bibuploadutils', opts=[]):
    """
    General purpose function that will write a MARCXML file and call bibupload
    on it.
    """
    if collection is None and record is None:
        return

    (file_out, filename) = open_temp_file(file_prefix)

    if collection is not None:
        file_out.write("<collection>")
        tot = 0
        for rec in collection:
            file_out.write(record_xml_output(rec))
            tot += 1
            if tot == CFG_MAX_RECORDS:
                file_out.write("</collection>")
                close_temp_file(file_out, filename)
                task_low_level_submission(
                    'bibupload', alias, mode, filename, *opts
                )

                (file_out, filename) = open_temp_file(file_prefix)
                file_out.write("<collection>")
                tot = 0
        file_out.write("</collection>")
    elif record is not None:
        tot = 1
        file_out.write(record_xml_output(record))

    close_temp_file(file_out, filename)
    if tot > 0:
        return task_low_level_submission(
            'bibupload', alias, mode, filename, *opts
        )
    return None
