<p data-toggle="tooltip" title="Publication date"><time itemprop="datePublished" datetime="{{ bfe_date(bfo, date_format='%Y-%m-%d') }}">{{ bfe_date(bfo, date_format="%d %B %Y") }}</time> <span class="pull-right">{{ bfe_openaire_pubtype(bfo, as_label="1") }} {{ bfe_openaire_access_rights(bfo, as_label="1") }}</span></p>
<h1 itemprop="name">{{ bfe_title(bfo, ) }}</span></h1>
<p id="authors_short">
{{ bfe_openaire_authors(bfo, relator_code_pattern="$", limit="25", interactive="yes", print_affiliations="no") }}
</p>
<p id="authors_long" class="hide">
{{ bfe_openaire_authors(bfo, relator_code_pattern="$", limit="25", interactive="yes", print_affiliations="yes", separator="<br />", affiliation_prefix="<br /><small>", affiliation_suffix="</small>") }}
</p>
<p><small><a href="#" class="muted" id="author_affiliations_link">(show affliations)</a></small></p>

{{ bfe_openaire_authors(bfo, relator_code_pattern='ths$', prefix='<p id="supervisors_short"><strong>Supervisor(s):</strong><br>', suffix='</p>', limit="25", interactive="yes", print_affiliations="no") }}
<p><span itemprop="description">{{ bfe_abstract(bfo, highlight="yes") }}</span></p>

{{ bfe_notes(bfo, prefix='<div class="alert">', suffix='</div>') }}
