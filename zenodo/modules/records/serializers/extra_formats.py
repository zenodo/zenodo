# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2019 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Extra Formats serializer."""

from __future__ import absolute_import, print_function

from flask import request

from zenodo.modules.deposit.extra_formats import ExtraFormats


class ExtraFormatsSerializer(object):
    """Extra Formats serializer.

    Serializes the extra formats types.
    """

    def serialize(self, pid, record, links_factory=None):
        """Include files for single record retrievals."""
        mimetype = request and request.args.get('mimetype')
        if not mimetype:
            return 'Extra format MIMEType not specified.'
        if mimetype not in ExtraFormats.mimetype_whitelist:
            return ('"{}" is not an acceptable extra format MIMEType.'
                    .format(mimetype))
        if mimetype in record.extra_formats:
            fileobj = record.extra_formats[mimetype]
            try:  # if an exception occurs, just let it be raised/logged
                fp = fileobj.obj.file.storage().open('rb')
                result = fp.read()
            finally:
                fp.close()
            return result
        return 'No extra formats available for this MIMEType.'
