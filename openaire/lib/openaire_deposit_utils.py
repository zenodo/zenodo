# -*- coding: utf-8 -*-
##
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

from invenio.openaire_deposit_config import CFG_METADATA_FIELDS
from invenio.webinterface_handler import wash_urlargd


def wash_form(form, publicationid=None):
    if publicationid is None:
        return wash_urlargd(form, dict([(field, (str, None)) for field in CFG_METADATA_FIELDS]))
    else:
        return wash_urlargd(form, dict([('%s_%s' % (field, publicationid), (str, None)) for field in CFG_METADATA_FIELDS]))


def strip_publicationid(fieldname, publicationid):
    return fieldname[:-len("_%s" % publicationid)]


def add_publicationid(fieldname, publicationid):
    return "%s_%s" % (fieldname, publicationid)


def namespaced_metadata2simple_metadata(namespaced_metadata, publicationid):
    return dict((strip_publicationid(key, publicationid), value) for key, value in namespaced_metadata.iteritems() if key.endswith('_%s' % publicationid))


def simple_metadata2namespaced_metadata(simple_metadata, publicationid):
    return dict((add_publicationid(key, publicationid), value) for key, value in simple_metadata.iteritems())
