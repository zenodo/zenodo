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
PAGES_ATTACHMENT_MAX_SIZE = 1000 * 1000 * 10  # 10 MB

#: Description maximum length.
PAGES_DESCRIPTION_MAX_LENGTH = 1000

#: Description minimum length.
PAGES_DESCRIPTION_MIN_LENGTH = 20

#: Email body template.
PAGES_EMAIL_BODY_TEMPLATE = 'zenodo_pages/email_body.html'

#: Email title template.
PAGES_EMAIL_TITLE_TEMPLATE = 'zenodo_pages/email_title.html'

#: Support confirmation email body.
PAGES_EMAIL_CONFIRM_BODY = """Thank you for contacting Zenodo support.

We have received your message, and we will do our best to get back to you
as soon as possible. This is an automated confirmation - please do not
reply to this email.

Zenodo Support Team
"""

#: Support confirmation email title.
PAGES_EMAIL_CONFIRM_TITLE = 'Zenodo support confirmation'

'zenodo_pages/email_confirm_title.html'

#: Issue category for contact form.
PAGES_ISSUE_CATEGORIES = [
    {
        'key': 'file-modification',
        'title': 'File modification',
        'description': (
            'All requests related to updating files in already published '
            'record(s). This includes file addition, removal or update of the '
            'files. '
            'Please consult our <a href="http://help.zenodo.org/#general">FAQ'
            '</a> to get familiar with the file update conditions.<br />'
            '<ol>'
            '<li>Please provide a justification for the file change in the '
            'description below.</li>'
            '<li>List the record(s) which you intend to update by the record '
            'URL, and specify which files need to be updated.</li>'
            '<li>Upload the new files here or provide a publicly-accessible '
            'URL(s) with the files, in the description below.</li>'
            '<li>Mention any use of the record(s) DOI in, e.g.: refer to the '
            'papers or social media posts.</li>'
            '</ol>'
        ),
        'recipients': ['info@zenodo.org'],
    },
    {
        'key': 'upload-quota',
        'title': 'File upload quota increase',
        'description': (
            'All requests for a quota increase beyond the 50GB limit. '
            'Please include the following information with your request:'
            '<ol>'
            '<li>The total size of your dataset, number of files and the '
            'largest file in the dataset.</li>'
            '<li>Information related to the organization, project or grant '
            'which was involved in the research, which produced the '
            'dataset.</li>'
            '<li>Information on the currently in-review or future papers that '
            'will cite this dataset (if applicable). If possible specify the '
            'journal or conferece.</li>'
            '</ol>'
        ),
        'recipients': ['info@zenodo.org'],
    },
    {
        'key': 'record-inactivation',
        'title': 'Record inactivation',
        'description': (
            'Requests related to record inactivation, either by the record '
            'owner or a third party. Please specify the record(s) in question '
            'by the URL(s), and reason for the inactivation.'
        ),
        'recipients': ['info@zenodo.org'],
    },
    {
        'key': 'openaire',
        'title': 'OpenAIRE',
        'description': (
            'All questions related to OpenAIRE reporting and grants. '
            'Before sending a request, make sure your problem was not '
            'already resolved, see OpenAIRE '
            '<a href="https://www.openaire.eu/support/faq">FAQ</a>. '
            'For questions unrelated to Zenodo, you should contact OpenAIRE '
            '<a href="https://www.openaire.eu/support/helpdesk">'
            'helpdesk</a> directly.'
        ),
        'recipients': ['info@zenodo.org'],
    },
    {
        'key': 'partnership',
        'title': 'Partnership, outreach and media',
        'description': (
            'All questions related to possible partnerships, outreach, '
            'invited talks and other official inquiries by media.'
            'If you are a journal, organization or conference organizer '
            'interested in using Zenodo as archive for your papers, software '
            'or data, please provide details for your usecase.'
            ),
        'recipients': ['info@zenodo.org'],
    },
    {
        'key': 'tech-support',
        'title': 'Security issue, bug or spam report',
        'description': (
            'Report a technical issue or a spam content on Zenodo.'
            'Please provide details on how to reproduce the bug. '
            'Upload any screenshots or files which are relevant to the issue '
            'or to means of reproducing it. Include error messages and '
            'error codes you might be getting in the description.<br /> '
            'For REST API errors, provide a minimal code which produces the '
            'issues. Use external services for scripts and long text'
            ', e.g.: <a href="https://gist.github.com/">GitHub Gist</a>. '
            '<strong>Do not disclose your password or REST API access tokens.'
            '</strong>'
            ),
        'recipients': ['info@zenodo.org'],
    },
    {
        'key': 'other',
        'title': 'Other',
        'description': (
            'Questions which do not fit into any other category.'),
        'recipients': ['info@zenodo.org'],
    },
]

#: Email address of sender.
PAGES_SENDER_EMAIL = 'info@zenodo.org'

#: Email address for support.
PAGES_SUPPORT_EMAIL = ['info@zenodo.org']
