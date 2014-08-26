{#
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
##
## ZENODO is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.
#}
<p><time itemprop="datePublished" datetime="{{ bfe_date(bfo, date_format='%Y-%m-%d') }}" data-toggle="tooltip" title="Publication date">{{ bfe_date(bfo, date_format="%d %B %Y") }}</time> <span class="pull-right">{{ bfe_openaire_pubtype(bfo, as_label="1") }} {{ bfe_openaire_access_rights(bfo, as_label="1") }}</span></p>
<h1 itemprop="name">{{ bfe_title(bfo, ) }}</h1>
<p id="authors_short" class="authors_list collapse in">
{{ bfe_openaire_authors(bfo, relator_code_pattern="$", limit="25", interactive="yes", print_affiliations="no") }}
</p>
<p id="authors_long" class="authors_list collapse">
{{ bfe_openaire_authors(bfo, relator_code_pattern="$", limit="25", interactive="yes", print_affiliations="yes", separator="<br>", affiliation_prefix="<br><small>", affiliation_suffix="</small>") }}
</p>

<p><small><a href="#" class="text-muted" data-toggle="collapse" data-target=".authors_list">(show affiliations)</a></small></p>

{{ bfe_openaire_authors(bfo, relator_code_pattern='ths$', prefix='<p id="supervisors_short"><strong>Supervisor(s):</strong><br>', suffix='</p>', limit="25", interactive="yes", print_affiliations="no") }}
<p><span itemprop="description">{{bfo.field('520__a').decode('utf8')|safe}}</span></p>

{{ bfe_notes(bfo, prefix='<div class="alert alert-warning">', suffix='</div>') }}