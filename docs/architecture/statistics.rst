..
    This file is part of Zenodo.
    Copyright (C) 2018 CERN.

    Zenodo is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Zenodo is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Zenodo; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

Statistics
----------

Events
~~~~~~

The usage statistics of the Zenodo records are generated from two different types of events:

* ``record-view``: this event is related to the view of a record and it's bounded to the ``record_viewed`` signal, which is
  emitted when one the following endpoints is accessed:

    * ``/record/<recid>``
    * ``/record/<recid>/export/<format>``

* ``file-download``: this event is related to the download a file of a record and it's is bounded to
  the  ``file_downloaded`` signal, which is emitted when one the following endpoints is accessed:

    * ``/record/<recid>/files/<filename>``
    * ``/api/record/<recid>/files/<filename>``

Every time a user views a record or downloads a file, the corresponding signal is emitted and the corresponding
event is created. In case an event fails to be emitted due to an exception raised in an event builder or to a failure
in sending the message to RabbitMQ, the request is not affected and a warning message is logged.

At the creation time each event keeps track of the following fields:

* record_id
* recid
* conceptrecid
* doi
* conceptdoi
* access_right
* resource_type
* communities
* owners
* timestamp
* referrer

We also capture the following user related fields for a limited period of time, i.e. until the event is processed
and the data are anonymized:

* ip_address
* user_agent
* user_id
* session_id

There are also some fields which are event specific.
For the ``file-download`` event we track:

* bucket_id
* file_id
* file_key
* size

While for the ``record-view`` event we track:

* pid_type
* pid_value

After an event is created, it is sent to a dedicated RabbitMQ queue. Each type of event has its own queue, so
different types of events can be processed separately.
The events which are in the queue are then consumed and processed by a Celery task. In this step the
flags ``is_machine`` and ``is_robot`` are added, the user is anonymized and the double-clicks are deleted. During the data
anonymization process the user related fields are deleted and replaced by the ``visitor_id`` and the ``unique_session_id``.
In case an event fails to be processed (e.g. malformed IP address), the event is skipped/lost and a warning message
is logged.
After the processing, the robot events are discarded for space saving, since they are not relevant for the statistics.
All the other processed events are saved in Elasticsearch.

