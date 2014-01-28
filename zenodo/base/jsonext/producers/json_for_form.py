# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013, 2014 CERN.
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


def produce(self, fields=None):
    """
    Export the record in marc format

    @param tags: list of tags to include in the output, if None or
                empty list all available tags will be included.
    """
    from invenio.modules.jsonalchemy.parser import get_producer_rules

    if not fields:
        fields = self.keys()

    out = {}

    for field in fields:
        if field.startswith('__'):
            continue
        try:
            rules = get_producer_rules(field, 'json_for_form', 'recordext')
            for rule in rules:
                field = self.get(rule[0], None)
                if field is None:
                    continue
                if not isinstance(field, list):
                    field = [field, ]
                for f in field:
                    for r in rule[1]:
                        tmp_dict = {}
                        for key, subfield in r[1].items():
                            if not subfield:
                                tmp_dict[key] = f
                            else:
                                try:
                                    tmp_dict[key] = f[subfield]
                                except:
                                    try:
                                        tmp_dict[key] = self._try_to_eval(
                                            subfield, value=f
                                        )
                                    except Exception as e:
                                        self['__error_messages.cerror[n]'] = \
                                            'Producer CError - Unable to ' \
                                            'produce %s - %s' % (field, str(e))
                        if tmp_dict:
                            for k, v in tmp_dict.items():
                                if isinstance(v, list):
                                    if k not in out:
                                        out[k] = []
                                    for element in v:
                                        out[k].append(element)
                                else:
                                    out[k] = v
        except KeyError:
            self['__error_messages.cerror[n]'] = \
                'Producer CError - No producer rule for field %s' % field
    return out
