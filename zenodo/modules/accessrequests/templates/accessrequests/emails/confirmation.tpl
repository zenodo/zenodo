{#
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
#}
Your access request has been successfully sent to the record owner. The decision whether to grant/deny access is solely under the responsibility of the record owner. Hence, please note that {{config.CFG_SITE_NAME}} staff are not involved in this decision.

Also note that the record owner is not allowed to charge you for granting access to the record hosted on {{config.CFG_SITE_NAME}}. Please notify us if this happens.

Record:
{{ record["title"] }}
{{ url_for('record.metadata', recid=record['recid'], _external=True) }}

Full name:
{{request.sender_full_name}}

Email address:
{{request.sender_email}}

Justification:
{{request.justification}}
