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

from wtforms import RadioField
from invenio.modules.deposit.field_base import WebDepositField
from invenio.modules.deposit.field_widgets import InlineListWidget,\
    BigIconRadioInput

__all__ = ['UploadTypeField']

UPLOAD_TYPES = [
    ('publication', 'Publication', [], 'fa fa-file-text-o fa-2x fa-fw'),
    ('poster', 'Poster', [], 'fa fa-columns fa-2x fa-fw'),
    ('presentation', 'Presentation', [], 'fa fa-group fa-2x fa-fw'),
    ('dataset', 'Dataset', [], 'fa fa-table fa-2x fa-fw'),
    ('image', 'Image', [], 'fa fa-bar-chart-o fa-2x fa-fw'),
    ('video', 'Video/Audio', [], 'fa fa-film fa-2x fa-fw'),
    ('software', 'Software', [], 'fa fa-cogs fa-2x fa-fw'),
]

UPLOAD_TYPE_ICONS = dict([(t[0], t[3]) for t in UPLOAD_TYPES])


def subtype_processor(form, field, submit=False, fields=None):
    form.image_type.flags.hidden = True
    form.image_type.flags.disabled = True
    form.publication_type.flags.hidden = True
    form.publication_type.flags.disabled = True
    if field.data == 'publication':
        form.publication_type.flags.hidden = False
        form.publication_type.flags.disabled = False
    elif field.data == 'image':
        form.image_type.flags.hidden = False
        form.image_type.flags.disabled = False


def set_license_processor(form, field, submit=False, fields=None):
    # Only run license processor, when the license wasn't specified.
    if fields and 'license' not in fields:
        if field.data == "dataset":
            if not form.license.flags.touched:
                form.license.data = 'cc-zero'
        elif field.data == "software":
            if not form.license.flags.touched:
                form.license.data = 'mit-license'
        else:
            if not form.license.flags.touched:
                form.license.data = 'cc-by'


class UploadTypeField(WebDepositField, RadioField):

    """
    Field to render a list
    """
    widget = InlineListWidget()
    option_widget = BigIconRadioInput(icons=UPLOAD_TYPE_ICONS)

    def __init__(self, **kwargs):
        kwargs['choices'] = [(x[0], x[1]) for x in UPLOAD_TYPES]
        kwargs['processors'] = [
            subtype_processor,
            set_license_processor,
        ]

        super(UploadTypeField, self).__init__(**kwargs)
