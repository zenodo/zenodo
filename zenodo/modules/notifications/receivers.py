# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2023 CERN.
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

"""Notifications receivers."""
from __future__ import absolute_import

from invenio_db import db
from invenio_webhooks.models import Receiver

from .tasks import process_peer_review
from .errors import NotificationAlreadyReceivedError, InvalidSenderError



class COARNotifyReceiver(Receiver):
    verify_sender = False

class PeerReviewReceiver(COARNotifyReceiver):
    verify_sender = False

    def run(self, event):
        """Process an event.
        """

        is_peer_review_event = \
            event.payload['type'][1] in ['coar-notify:ReviewAction']

        if is_peer_review_event:
            try:
                peer_review = PeerReview.create(event)
                db.session.commit()

                if current_app.config['ZENODO_NOTIFICATIONS_PROCESS_PEER_REVIEWS']:
                    process_peer_review.delay(
                        peer_review.id,
                        verify_sender=self.verify_sender
                    )
            except NotificationAlreadyReceivedError as e:
                event.response_code = 409
                event.response = dict(message=str(e), status=409)
            except InvalidSenderError as e:
                event.response = 403
                event.response = dict(message=str(e), status=403)
