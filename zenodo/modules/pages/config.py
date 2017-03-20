# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Configuration for Zenodo Pages."""

from __future__ import absolute_import, print_function

#: Maximum size of attachment in contact form.
PAGES_ATTACHMENT_MAX_SIZE = 1000 * 1000 * 10 # 10 MB

#: Description minimum length.
PAGES_DESCRIPTION_MIN_LENGTH = 20

#: Description maximum length.
PAGES_DESCRIPTION_MAX_LENGTH = 1000

#: Email body template.
PAGES_EMAIL_BODY_TEMPLATE = 'zenodo_pages/email_body.html'

#: Email title template.
PAGES_EMAIL_TITLE_TEMPLATE = 'zenodo_pages/email_title.html'

#: Issue category for contact form.
PAGES_ISSUE_CATEGORY = [
    ('Technical Support', "Please describe the error you are getting, "\
     "include any error messages or link to screenshots which might be relevant"),
    ('File upload request', "Please include the URL of the updated file, "\
     "and specify which record and file you want to replace. Please use publicly accessible URLs."),
    ('Others', "Specify the issue"),
]

#: Email address for support.
PAGES_SUPPORT_EMAIL = ['info@zenodo.org', ]

#: Email address of sender.
PAGES_SENDER_EMAIL = 'info@zenodo.org'
