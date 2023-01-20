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

"""Notification errors."""


class NotificationError(Exception):
    """General notification error."""


class InvalidSenderError(NotificationError):
    """Invalid notification sender error."""

    message = u'Invalid sender for event'

    def __init__(self, event=None, user=None, message=None):
        """Constructor."""
        super(InvalidSenderError, self).__init__(message or self.message)
        self.event = event
        self.user = user


class NotificationAlreadyReceivedError(NotificationError):
    """Notification already released error."""

    message = u'The notification has already been received.'

    def __init__(self, notification=None, message=None):
        """Constructor."""
        super(NotificationAlreadyReceivedError, self).__init__(
            message or self.message)
        self.notification = notification


class InvalidNotificationMetadataError(NotificationError):
    """Invalid metadata error."""

    message = u'The metadata is not valid JSON.'

    def __init__(self, metadata=None, message=None):
        """Constructor."""
        super(InvalidNotificationMetadataError, self).__init__(
            message or self.message)
        self.metadata = metadata



class RecordNotFoundError(NotificationError):
    """Record not found."""

    message = u'The corresponding record was not found.'

    def __init__(self, doi=None, message=None):
        """Constructor."""
        super(RecordNotFoundError, self).__init__(
            message or self.message)
        self.doi = doi
