
{{ bfe_openaire_altmetric(bfo, prefix='<div class="well metadata">', suffix="</div>", badgetype='donut', details='left', no_script='1') }}

<div class="well metadata">
  <dl>
    {{ bfe_creation_date(bfo, date_format="%d %M %Y", prefix='<dt>Upload date:</dt><dd>', suffix='</dd>') }}
    {{ bfe_date(bfo, date_format='%d %B %Y', prefix='<dt>Publication date:</dt><dd>', suffix='</dd>') }}
    {{ bfe_openaire_access_rights(bfo, only_restrictions="yes") }}
    {{ bfe_doi(bfo, prefix='<dt>DOI:</dt><dd>', suffix='</dd>') }}
    {{ bfe_isbn(bfo, prefix='<dt>ISBN:</dt><dd>', suffix='</dd>') }}
    {{ bfe_report_numbers(bfo, prefix='<dt>Report number(s):</dt><dd>', suffix='</dd>') }}
    {{ bfe_keywords(bfo, prefix='<dt>Keyword(s):</dt><dd>', suffix='</dd>', keyword_prefix='<span class="label" itemprop="keywords">', keyword_suffix='</span>', separator=' ') }}
    {{ bfe_publi_info(bfo, prefix='<dt>Published in:</dt><dd>', suffix='</dd>') }}
    {{ bfe_openaire_published_in_book(bfo, prefix='<dt>Published in:</dt><dd>', suffix='</dd>') }}
    {{ bfe_publisher(bfo, prefix='<dt>Publisher:</dt><dd>', suffix='</dd>') }}
    {{ bfe_place(bfo, prefix='<dd>', suffix='</dd>') }}
    {{ bfe_field(bfo, escape="0", tag="536__a", prefix='<dt>Funded by:</dt><dd>', suffix='</dd>', instances_separator='<br />') }}
    {{ bfe_openaire_university(bfo, prefix='<dt>Thesis:</dt><dd>', suffix='</dd>') }}
    {{ bfe_openaire_meeting(bfo, prefix='<dt>Meeting:</dt><dd>', suffix='</dd>') }}
    {{ bfe_pagination(bfo, prefix='<dt>Pages:</dt><dd>', suffix='</dd>', default='', escape='') }}
    {{ bfe_openaire_related_dois(bfo, type='pub', prefix='<dt>Related publications:</dt><dd>', suffix='</dd>') }}
    {{ bfe_openaire_related_dois(bfo, type='data', prefix='<dt>Related datasets:</dt><dd>', suffix='</dd>') }}
    {{ bfe_appears_in_collections(bfo, prefix='<dt>Collections:</dt><dd>', suffix='</dd>') }}
    {{ bfe_openaire_license(bfo, prefix='<dt>License (for files):</dt><dd>', suffix='</dd>') }}
  </dl>
</div>