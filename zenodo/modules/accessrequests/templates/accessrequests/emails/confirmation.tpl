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
Your access request has been completed and sent to the owner of the record. It is fully the decision of the owner if they grant/deny access. In particular, Zenodo staff is not involved in this decision.

Also note that the owner not allowed to charge you for granting access to the record hosted on Zenodo. Please notify us if this happens.

Record:
{{ record["title"] }}
{{ url_for('record.metadata', recid=record['recid'], _external=True) }}

Full name:
{{request.sender_full_name}}

Email address:
{{request.sender_email}}

Justification:
{{request.justification}}
