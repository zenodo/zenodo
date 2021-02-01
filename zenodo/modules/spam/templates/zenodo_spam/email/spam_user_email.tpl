{#
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
-#}
{% if community %}
{% set content_text = 'the creation of the community with ID: ' + community.id %}
{% else %}
{% set content_text = 'the publication of your deposit titled: ' + deposit.title %}
{% endif %}

Our spam protection system has classified {{ content_text }} as potential spam content.
As a preventive measure, we have deactivated your user account.

We sincerely apologize if this was a mistake, in which case, please contact us on our support line at https://zenodo.org/support.
