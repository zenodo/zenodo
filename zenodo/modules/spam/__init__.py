# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Simple spam checks."""

import re

from flask import current_app


def check_email_domain(user_email):
    """Check if domain usually have spammers."""
    for domain in current_app.config.get('SPAM_DOMAINS'):
        if user_email.endswith(domain):
            return True
    return False


def check_text(text, extra_matches=None, extra_tokens=None):
    """Check text."""
    text = text.lower()

    text_re = re.compile("(%s)" % "|".join(
        current_app.config.get('SPAM_MATCHERS')+(extra_matches or [])))

    if text_re.match(text):
        return True

    for token in current_app.config.get('SPAM_TOKENS')+(extra_tokens or []):
        if token in text:
            return True

    return False
