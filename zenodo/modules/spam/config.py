# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2020 CERN.
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

"""Configuration for Zenodo Spam."""

from flask import abort, current_app, flash
from flask_login import logout_user
from invenio_accounts.models import User
from invenio_accounts.sessions import delete_user_sessions
from invenio_db import db

from zenodo.modules.spam.utils import send_spam_admin_email, \
    send_spam_user_email


def default_spam_handling(deposit=None, community=None):
    """Default actions to counter spam detected record."""
    if deposit:
        user = User.query.get(deposit['_deposit']['owners'][0])
    if community:
        user = community.owner
        community.description = '--SPAM--' + community.description
        if community.oaiset:
            db.session.delete(community.oaiset)
        community.delete()
    user.active = False
    delete_user_sessions(user)
    logout_user()
    db.session.add(user)
    db.session.commit()
    send_spam_user_email(user.email, deposit=deposit, community=community)
    if current_app.config['ZENODO_SPAM_EMAIL_ADMINS']:
        send_spam_admin_email(user, deposit=deposit)
    if deposit:
        error_message = \
            ('Our spam protection system has classified your upload as a '
             'potential spam attempt. As a preventive measure and due to '
             'significant increase in spam, we have therefore deactivated '
             'your user account and logged you out of Zenodo. Your upload has '
             'not been published. If you think this is a mistake, please  '
             'contact our support.')
    if community:
        error_message = \
            ('Our spam protection system has classified your community as a '
             'potential spam attempt. As a preventive measure and due to '
             'significant increase in spam, we have therefore deactivated '
             'your user account and logged you out of Zenodo. Your community '
             'has not been created. If you think this is a mistake, please  '
             'contact our support.')
    flash(error_message, category='warning')
    abort(400, error_message)


# Function handling deposit metadata detected as spam when publishing
ZENODO_SPAM_HANDLING_ACTIONS = default_spam_handling

# Spam model for record predictions
ZENODO_SPAM_MODEL_LOCATION = None

# Float number defining the probability over which a record is considered spam
ZENODO_SPAM_THRESHOLD = 0.5

# Should send email to Admins for automatically blocked users
ZENODO_SPAM_EMAIL_ADMINS = True

# Timeout for spam check task before it bypasses the check
ZENODO_SPAM_CHECK_TIMEOUT = 8

# Number of valid existing records and communities to skip the spam check
ZENODO_SPAM_SKIP_CHECK_NUM = 5

# Preload spam model on Celery app initialization
ZENODO_SPAM_MODEL_PRELOAD = False

ZENODO_SPAM_DOMAINS_FORBIDDEN_PATH = None
"""Path to a file with the list of forbidden email domains."""

ZENODO_SPAM_DOMAINS_SAFELIST_PATH = None
"""Path to a file with the list of safelisted domains."""
