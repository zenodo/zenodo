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


__all__ = ['UploadTypeField']

UPLOAD_TYPES = [
    ('publication', 'Publication', [], 'file-alt'),
    ('poster', 'Poster', [], 'columns'),
    ('presentation', 'Presentation', [], 'group'),
    ('dataset', 'Dataset', [], 'table'),
    #('Software', []),
    ('image', 'Image', [], 'bar-chart'),
    ('video', 'Video/Audio', [], 'film'),
    ('software', 'Software', [], 'cogs'),
]

UPLOAD_TYPE_ICONS = dict([(x[0], x[3]) for x in UPLOAD_TYPES])


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
        super(RadioInput, self).__init__(**kwargs)

    def __call__(self, field, **kwargs):
        if field.checked:
            kwargs['checked'] = u'checked'

        html = super(RadioInput, self).__call__(field, **kwargs)
        icon = self.choices_icons.get(field._value(), '')
        if icon:
            html = """<i class="icon-%s icon-2x"></i><br />%s</br>%s""" % (icon, field.label.text, html)
        return html


class UploadTypeField(RadioField):
    """
    Field to render a list
    """
    widget = InlineListWidget()
    option_widget = BigIconRadioInput(icons=UPLOAD_TYPE_ICONS)

    def __init__(self, **kwargs):
        kwargs['choices'] = [(x[0], x[1]) for x in UPLOAD_TYPES]
        super(UploadTypeField, self).__init__(**kwargs)
