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

"""Forms for spam deletion module."""

from __future__ import absolute_import, print_function

from celery.exceptions import TimeoutError
from elasticsearch_dsl import Q
from flask import current_app, render_template
from flask_babelex import gettext as _
from flask_mail import Message
from flask_principal import ActionNeed
from invenio_access import Permission
from invenio_communities.models import Community
from invenio_mail.tasks import send_email
from invenio_search.api import RecordsSearch
from werkzeug.exceptions import HTTPException

from zenodo.modules.spam.tasks import check_metadata_for_spam


def send_spam_user_email(recipient, deposit=None, community=None):
    """Send email notification to blocked user after spam detection."""
    msg = Message(
        _("Your Zenodo activity has been automatically marked as Spam."),
        sender=current_app.config.get('SUPPORT_EMAIL'),
        recipients=[recipient],
    )
    msg.body = render_template(
        "zenodo_spam/email/spam_user_email.tpl",
        community=community,
        deposit=deposit
    )
    send_email.delay(msg.__dict__)


def send_spam_admin_email(user, deposit=None, community=None):
    """Send email notification to admins for a spam detection."""
    msg = Message(
        _("Zenodo activity marked as spam."),
        sender=current_app.config.get('SUPPORT_EMAIL'),
        recipients=[current_app.config.get('ZENODO_ADMIN_EMAIL')],
    )
    msg.body = render_template(
        "zenodo_spam/email/spam_admin_email.tpl",
        user=user,
        deposit=deposit,
        community=community
    )
    send_email.delay(msg.__dict__)


def check_and_handle_spam(community=None, deposit=None, retry=True):
    """Checks community/deposit metadata for spam."""
    try:
        if current_app.config.get('ZENODO_SPAM_MODEL_LOCATION'):
            if community:
                task = check_metadata_for_spam.delay(
                    community_id=community.id)
                user_id = community.id_user
            if deposit:
                task = check_metadata_for_spam.delay(dep_id=str(deposit.id))
                user_id = deposit['owners'][0]
            spam_proba = task.get(timeout=current_app.config[
                'ZENODO_SPAM_CHECK_TIMEOUT'])
        else:
            spam_proba = 0
        if spam_proba > current_app.config['ZENODO_SPAM_THRESHOLD']:
            if not Permission(ActionNeed('admin-access')).can():
                user_records = RecordsSearch(index='records').query(
                    Q('query_string', query="owners:{}".format(
                        user_id))).count()
                user_communities = Community.query.filter_by(
                        id_user=user_id).count()
                if community:
                    # Ignore the newly created community
                    user_communities = user_communities - 1
                current_app.logger.warning(
                    u'Found spam upload',
                    extra={
                        'depid': deposit.id if deposit else None,
                        'comid': community.id if community else None
                    }
                )
                if not (user_records + user_communities >
                        current_app.config['ZENODO_SPAM_SKIP_CHECK_NUM']):
                    current_app.config['ZENODO_SPAM_HANDLING_ACTIONS'](
                        community=community, deposit=deposit)
    except HTTPException:
        raise
    except TimeoutError:
        if retry:
            check_and_handle_spam(
                community=community, deposit=deposit, retry=False)
        else:
            current_app.logger.exception(
                u'Could not check for spam',
                extra={
                    'depid': deposit.id if deposit else None,
                    'comid': community.id if community else None
                }
            )
    except Exception:
        current_app.logger.exception(
            u'Could not check for spam',
            extra={
                'depid': deposit.id if deposit else None,
                'comid': community.id if community else None
            }
        )
