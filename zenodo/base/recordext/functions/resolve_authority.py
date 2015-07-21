# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


"""Resolve Authority helper functions."""


def extract_authority_value(value, authority_control):
    """Extract value of authority control.

    :param value: single authority control value to extract
    :param str authority_control: name of the authority control to be extracted
    :return: extracted value or empty string
    """
    if (value or '').startswith("(%s)" % authority_control):
        i = len(authority_control) + 2
        return value[i:]
    else:
        return ''


def resolve_authority(values, authority_control):
    """Determine value of a authority control field.

    It tries to find a value of given authority control in a list of values.

    :param value: list containing values of authority controls or
                  single authority control value
    :param str authority_control: name of the authority control
    :return: extracted value or empty string
    """
    if not isinstance(values, list):
        values = [values]
    for value in values:
        result = extract_authority_value(value, authority_control)
        if result:
            if authority_control == "gnd":
                return "gnd:{0}".format(result)
            return result
    return ''
