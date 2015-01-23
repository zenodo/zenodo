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
You've got a new access request. To accept/reject the request, please open the link below:

{{url_for('zenodo_accessrequests_settings.accessrequest',
          request_id=request.id, _external=True, _scheme='https')}}

Record:
{{ record["title"] }}
{{ url_for('record.metadata', recid=record['recid'], _external=True) }}

Full name:
{{request.sender_full_name}}

Email address:
{{request.sender_email}}

Justification:
{{request.justification}}
