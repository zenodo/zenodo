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

"""Configuration for Zenodo Support."""

from __future__ import absolute_import, print_function

#: Maximum size of attachment in contact form.
SUPPORT_ATTACHMENT_MAX_SIZE = 1000 * 1000 * 10  # 10 MB

#: Description maximum length.
SUPPORT_DESCRIPTION_MAX_LENGTH = 5000

#: Description minimum length.
SUPPORT_DESCRIPTION_MIN_LENGTH = 20

#: Email body template.
SUPPORT_EMAIL_BODY_TEMPLATE = 'zenodo_support/email_body.html'

#: Email title template.
SUPPORT_EMAIL_TITLE_TEMPLATE = 'zenodo_support/email_title.html'

#: Support confirmation email body.
SUPPORT_EMAIL_CONFIRM_BODY = """Thank you for contacting Zenodo support.

We have received your message, and we will do our best to get back to you as \
soon as possible.
This is an automated confirmation of your request, please do not reply to this\
 email.

Zenodo Support
https://zenodo.org
"""

#: Support confirmation email title.
SUPPORT_EMAIL_CONFIRM_TITLE = 'Zenodo Support'

'zenodo_support/email_confirm_title.html'

#: Issue category for contact form.
SUPPORT_ISSUE_CATEGORIES = [
    {
        'key': 'file-modification',
        'title': 'File modification',
        'description': (
            'All requests related to updating files in already published '
            'record(s). This includes new file addition, file removal or '
            'file replacement. '
            'Before sending a request, please consider creating a '
            '<a href="http://help.zenodo.org/#versioning">new version</a> '
            'of your upload. Please first consult our '
            '<a href="http://help.zenodo.org/#general">FAQ</a> to get familiar'
            ' with the file update conditions, to see if your case is '
            'eligible.<br /><br />'
            'You request has to contain <u>all</u> of the points below:'
            '<ol>'
            '<li>Provide a justification for the file change in the '
            'description.</li>'
            '<li>Mention any use of the record(s) DOI in publications or '
            'online, e.g.: list papers that cite your record and '
            'provide links to posts on blogs and social media. '
            'Otherwise, state that to the best of your knowledge the DOI has '
            'not been used anywhere.</li>'
            '<li>Specify the record(s) you want to update <u>by the Zenodo'
            ' URL</u>, e.g.: "https://zenodo.org/record/8428".<br />'
            "<u>Providing only the record's title, publication date or a "
            "screenshot with search result is not explicit enough</u>.</li>"
            '<li>If you want to delete or update a file, specify it '
            '<u>by its filename</u>, and mention if you want the name to '
            'remain as is or changed (by default the filename of the new '
            'file will be used).</li>'
            '<li>Upload the new files below or provide a publicly-accessible '
            'URL(s) with the files in the description.</li>'
            '</ol>'
            '<b><u>Not providing full information on any of the points above '
            'will significantly slow down your request resolution</u></b>, '
            'since our support staff will have to reply back with a request '
            'for missing information.'
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
            'largest file in the dataset. When referring to file sizes'
            ' use <a href="https://en.wikipedia.org/wiki/IEEE_1541-2002">'
            'SI units</a></li>'
            '<li>Information related to the organization, project or grant '
            'which was involved in the research, which produced the '
            'dataset.</li>'
            '<li>Information on the currently in-review or future papers that '
            'will cite this dataset (if applicable). If possible specify the '
            'journal or conference.</li>'
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
            '<a href="https://www.openaire.eu/faqs">FAQ</a>. '
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
            'Report a technical issue or a spam content on Zenodo. '
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
SUPPORT_SENDER_EMAIL = 'info@zenodo.org'

#: Name of the sender
SUPPORT_SENDER_NAME = 'Zenodo'

#: Email address for support.
SUPPORT_SUPPORT_EMAIL = ['info@zenodo.org']
