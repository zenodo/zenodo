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
    from invenio.base.utils import try_to_eval

    from invenio.modules.jsonalchemy.parser import get_producer_rules
    from invenio.modules.jsonalchemy.registry import functions

    if not fields:
        fields = self.keys()

    out = {}

    for field in fields:
        if field.startswith('__') or self.get(field) is None:
            continue
        json_id = self.meta_metadata[field]['json_id']
        values = self.get(field)
        if not  isinstance(values, (list, tuple)):
            values = (values, )
        for value in values:
            try:
                rules = get_producer_rules(json_id, 'json_for_form', 'recordext')
                for rule in rules:
                    tags = rule[0] if isinstance(rule[0], tuple) \
                                        else (rule[0], )
                    if tags and not any([tag in tags \
                            for tag in self.meta_metadata[field]['function']]):
                        continue
                    tmp_dict = {}
                    for key, subfield in rule[1].items():
                        if not subfield:
                            tmp_dict[key] = value
                        else:
                            try:
                                tmp_dict[key] = value[subfield]
                            except:
                                try:
                                    tmp_dict[key] = try_to_eval(subfield,
                                        functions(
                                            self.additional_info.namespace),
                                        value=value, self=self)
                                except ImportError:
                                    pass
                                except Exception as e:
                                    self.continuable_errors.append(
                                        "Producer CError - Unable to produce "
                                        "'%s'.\n %s" % (field, str(e)))

                    if tmp_dict:
                        for k, v in tmp_dict.items():
                            if isinstance(v, list):
                                if k not in out:
                                    out[k] = []
                                for element in v:
                                    out[k].append(element)
                            else:
                                out[k] = v
            except KeyError as e:
                self.continuable_errors.append(
                    "Producer CError - Unable to produce '%s' (No rule found).\n %s"
                    % (field, str(e)))
    return out
