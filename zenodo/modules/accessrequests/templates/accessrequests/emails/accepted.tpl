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
Your access request has been accepted by the record owner. To access the record please open your private link:

{{record_link}}

{%- if expires_at %}
The link expires on {{expires_at}}.{% endif -%}
{% if message %}

Message from owner:
{{message}}{% endif %}

IMPORTANT! Do not share above link. The link is private to you. Instead please redirect collaborators to request a link for themselves.

Please note that the owner may revoke the link at any anytime without prior notification.
