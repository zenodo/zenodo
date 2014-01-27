<p data-toggle="tooltip" title="Publication date"><time itemprop="datePublished" datetime="{{ bfe_date(bfo, date_format='%Y-%m-%d') }}">{{ bfe_date(bfo, date_format="%d %B %Y") }}</time> <span class="pull-right">{{ bfe_openaire_pubtype(bfo, as_label="1") }} {{ bfe_openaire_access_rights(bfo, as_label="1") }}</span></p>
<h1 itemprop="name">{{ bfe_title(bfo, ) }}</h1>
<p id="authors_short" class="authors_list collapse in">
{{ bfe_openaire_authors(bfo, relator_code_pattern="$", limit="25", interactive="yes", print_affiliations="no") }}
</p>
<p id="authors_long" class="authors_list collapse">
{{ bfe_openaire_authors(bfo, relator_code_pattern="$", limit="25", interactive="yes", print_affiliations="yes", separator="<br>", affiliation_prefix="<br><small>", affiliation_suffix="</small>") }}
</p>

<p><small><a href="#" class="text-muted" data-toggle="collapse" data-target=".authors_list">(show affliations)</a></small></p>

{{ bfe_openaire_authors(bfo, relator_code_pattern='ths$', prefix='<p id="supervisors_short"><strong>Supervisor(s):</strong><br>', suffix='</p>', limit="25", interactive="yes", print_affiliations="no") }}
<p><span itemprop="description">{{bfo.field('520__a').decode('utf8')|safe}}</span></p>

{{ bfe_notes(bfo, prefix='<div class="alert alert-warning">', suffix='</div>') }}