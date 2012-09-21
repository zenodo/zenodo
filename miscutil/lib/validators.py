## This file is part of Invenio.
## Copyright (C) 2012 CERN.
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

"""
Validation functions
"""


def _convert_x_to_10(x):
    if x != 'X':
        return int(x)
    else:
        return 10


def is_isbn10(val):
    """
    Test if argument is an ISBN-10 number

    Courtesy Wikipedia:
    http://en.wikipedia.org/wiki/International_Standard_Book_Number
    """
    val = val.replace("-", "").replace(" ", "")
    if len(val) != 10:
        return False
    r = sum([(10 - i) * (_convert_x_to_10(x)) for i, x in enumerate(val)])
    return not (r % 11)


def is_isbn13(val):
    """
    Test if argument is an ISBN-13 number

    Courtesy Wikipedia:
    http://en.wikipedia.org/wiki/International_Standard_Book_Number
    """
    val = val.replace("-", "").replace(" ", "")
    if len(val) != 13:
        return False
    total = sum([int(num) * weight for num, weight in zip(val, (1, 3) * 6)])
    ck = (10 - total) % 10
    return ck == int(val[-1])


def is_isbn(val):
    """ Test if argument is an ISBN-10 or ISBN-13 number """
    return is_isbn10(val) or is_isbn13(val)


def is_all_uppercase(val):
    """ Returns true if more than 75% of the characters are upper-case """
    uppers = 0
    for c in val:
        if c.isupper():
            uppers += 1
    if 1.0 * uppers / len(val) > 0.75:
        return True
    else:
        return False


def is_probably_list(val):
    """ Returns true if string looks like a list - e.g. a, b, c, or a; b; c;"""
    if val:
        LIMIT = 2
        counts = {';': 0, '-': 0, ',': 0, }
        separators = counts.keys()
        warn = False
        for c in val:
            for sep in separators:
                if c == sep:
                    counts[sep] += 1
        for sep, n in counts.items():
            if n >= LIMIT:
                return True
