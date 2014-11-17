{#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013, 2014 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.
#}

<div class="media htmlbrief">
    <span class="pull-left hidden-sm">
        {{ bfe_icon(bfo, subformat_re='icon-90') }}
    </span>
    <span class="pull-right hidden-sm">
        {{ bfe_openaire_altmetric(bfo, badgetype='donut', popover='left', no_script='1', prefix="<br>") }}
    </span>
    <div class="media-body">
        <span class="label label-info" data-toggle="tooltip" title="Publication date">{{ bfe_date(bfo, date_format='%d %B %Y') }}</span>
        {{ bfe_openaire_pubtype(bfo, as_label="1", brief="1") }}
        {{ bfe_openaire_access_rights(bfo, as_label="1", brief="1") }}
        <br>
        <h4 class="media-heading muted_a"><a href="{{ bfe_record_url(bfo, ) }}">{{ bfe_title_brief(bfo, highlight="no") }}</a></h4>
        <p>{{ bfe_authors(bfo, limit="4", extension="; et al. ", highlight="no") }}</p>
        <p class="muted_a"><a href="{{ bfe_record_url(bfo, ) }}">{{ bfo.field('520__a').decode('utf8')|striptags|truncate }}</a></p>
        {% if bfo.field('8560_y') %}<small class="text-muted">Uploaded by {{bfo.field('8560_y').decode('utf8')}} on {{ bfe_creation_date(bfo, date_format="%d %M %Y") }}.</small>{% endif %}
    </div>
</div>
