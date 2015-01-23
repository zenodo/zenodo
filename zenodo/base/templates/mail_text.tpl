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
{%- block mail_header -%}
{% if header %}{{ header }}{% else %}{{ _("Hello:") }}{% endif %}
{% endblock -%}
{%- block mail_content -%}
{{ content }}
{% endblock -%}
{%- block mail_footer %}
{% if footer %}{{ footer }}{% else %}


{{ _("Best regards") }}
--
{{ config.CFG_SITE_NAME_INTL.get(g.ln, config.CFG_SITE_NAME) }} <{{ config.CFG_SITE_URL }}>
{{ _("Need human intervention?  Contact") }} <{{ config.CFG_SITE_SUPPORT_EMAIL }}>
{% endif %}
{% endblock -%}
