# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012, 2013 CERN.
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

from wtforms import RadioField
from wtforms.widgets import HTMLString, RadioInput
from invenio.webdeposit_field import WebDepositField


__all__ = ['UploadTypeField']

UPLOAD_TYPES = [
    ('publication', 'Publication', [], 'file-alt'),
    ('poster', 'Poster', [], 'columns'),
    ('presentation', 'Presentation', [], 'group'),
    ('dataset', 'Dataset', [], 'table'),
    #('Software', []),
    ('image', 'Image', [], 'bar-chart'),
    ('video', 'Video/Audio', [], 'film'),
    #('audio', 'Audio', [], 'volume-up'),
]

UPLOAD_TYPE_ICONS = dict([(t[0], t[3]) for t in UPLOAD_TYPES])


class InlineListWidget(object):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = [u'<ul class="inline">']
        for subfield in field:
            html.append(u'<li class="span1"><label>%s</label></li>' % (subfield()))
        html.append(u'</ul>')
        return HTMLString(u''.join(html))


class BigIconRadioInput(RadioInput):
    """
    Render a single radio button with icon.

    This widget is most commonly used in conjunction with ListWidget or some
    other listing, as singular radio buttons are not very useful.
    """
    input_type = 'radio'

    def __init__(self, icons={}, **kwargs):
        self.choices_icons = icons
        super(BigIconRadioInput, self).__init__(**kwargs)

    def __call__(self, field, **kwargs):
        if field.checked:
            kwargs['checked'] = u'checked'

        html = super(BigIconRadioInput, self).__call__(field, **kwargs)
        icon = self.choices_icons.get(field._value(), '')
        if icon:
            html = """<i class="icon-%s icon-2x"></i><br />%s</br>%s""" % (icon, field.label.text, html)
        return html


class UploadTypeField(WebDepositField, RadioField):
    """
    Field to render a list
    """
    widget = InlineListWidget()
    option_widget = BigIconRadioInput(icons=UPLOAD_TYPE_ICONS)

    def __init__(self, **kwargs):
        kwargs['choices'] = [(x[0], x[1]) for x in UPLOAD_TYPES]
        super(UploadTypeField, self).__init__(**kwargs)

    def post_process(self, form, extra_processors=[], submit=False):
        # Hide/show subtype fields.
        form.image_type.flags.hidden=True
        form.image_type.flags.disabled=True
        form.publication_type.flags.hidden=True
        form.publication_type.flags.disabled=True
        if self.data == 'publication':
            form.publication_type.flags.hidden=False
            form.publication_type.flags.disabled=False
        elif self.data == 'image':
            form.image_type.flags.hidden=False
            form.image_type.flags.disabled=False

        # Set value of license field
        if self.data == "dataset":
            if form.license.data == 'cc-by': #i.e user likely didn't change default
                form.license.data = 'cc-zero'
        else:
            if form.license.data in ['cc-zero','cc-by']: #i.e user likely didn't change default
                form.license.data = 'cc-by'

        super(UploadTypeField, self).post_process(form, extra_processors=extra_processors)