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

"""BibFormat element - QR code generator
"""

import os
from flask import current_app

try:
    import qrcode
    from PIL import Image
    HAS_QR = True
except ImportError:
    HAS_QR = False

try:
    import hashlib
    HAS_HASHLIB = True
except ImportError:
    import md5
    HAS_HASHLIB = False


def _get_record_hash(link):
    """
    Generate a record hash including CFG_SITE_URL so that
    if CFG_SITE_URL is updated, the QR-code image is invalidated.
    """
    if HAS_HASHLIB:
        m = hashlib.md5()
    else:
        m = md5.new()
    m.update(link)
    return m.hexdigest()[:8].lower()


def format_element(bfo, width="100"):
    """
    """
    if not HAS_QR:
        return ""

    width = int(width)
    CFG_SITE_SECURE_URL = current_app.config['CFG_SITE_SECURE_URL']
    CFG_WEBDIR = current_app.config['CFG_WEBDIR']
    CFG_SITE_RECORD = current_app.config['CFG_SITE_RECORD']

    bibrec_id = bfo.control_field("001")
    link = "%s/%s/%s" % (CFG_SITE_SECURE_URL, CFG_SITE_RECORD, bibrec_id)
    hash_val = _get_record_hash(link)

    filename = "%s_%s.png" % (bibrec_id, hash_val)
    filename_url = "/img/qrcodes/%s" % filename
    filename_path = os.path.join(CFG_WEBDIR, "img/qrcodes/%s" % filename)

    if not os.path.exists(filename_path):
        if not os.path.exists(os.path.dirname(filename_path)):
            os.makedirs(os.path.dirname(filename_path))

        img = qrcode.make(link)
        img._img = img._img.convert("RGBA")
        img._img = img._img.resize((width, width), Image.ANTIALIAS)
        img.save(filename_path, "PNG")

    return """<img src="%s" width="%s" alt="QR-code for easy mobile access" />""" % (filename_url, width)


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
