# -*- coding: utf-8 -*-
#
# This file is part of ZENODO.
# Copyright (C) 2014 CERN.
#
# ZENODO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ZENODO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


"""
PreservationMeter tasks for Zenodo
"""

# from __future__ import absolute_import

# from celery.utils.log import get_task_logger
# from invenio.celery import celery
# from invenio.modules.webhooks.models import Event

# logger = get_task_logger(__name__)
from .api import calculate_score


def calculate_preservation_score(recid):
    """ Calculates the preservation score of a given record """
    calculate_score(recid)


# @celery.task(ignore_result=True)
# def handle_inspire_payload(event_state):
#     """
#     """
#     e = Event()
#     e.__setstate__(event_state)

#     #e.user_id
#     #e.payload

#     pass
