{{- bfe_meta(bfo, tag="245__a", name="citation_title") -}}
{{- bfe_meta(bfo, tag="100__a", tag_name="first author", name="citation_author") -}}
{{- bfe_meta(bfo, tag="700__a", tag_name="additional author", name="citation_author") -}}
{{- bfe_meta(bfo, tag="260__b", name="citation_publisher") -}}
{{- bfe_meta(bfo, tag="260__c", name="citation_publication_date") -}}
{{- bfe_meta(bfo, tag="0247_a", tag_name="doi", name="citation_doi") -}}
{{- bfe_meta(bfo, tag="909C4p", tag_name="journal title", name="citation_journal_title") -}}
{{- bfe_meta(bfo, tag="909C4v", tag_name="journal volume", name="citation_volume") -}}
{{- bfe_meta(bfo, tag="909C4c", tag_name="journal page", name="citation_firstpage") -}}
{{- bfe_meta(bfo, tag_name="journal lastpage", name="citation_lastpage") -}}
{{- bfe_meta(bfo, tag="909C4i", tag_name="journal issue", name="citation_issue") -}}
{{- bfe_meta(bfo, tag="711__a", name="citation_conference") -}}
{{- bfe_meta(bfo, tag_name="abstract url", tag="8564_a", name="citation_abstract_url") -}}
{{- bfe_meta(bfo, tag_name="date", tag="269__c", name="citation_date") -}}
{{- bfe_meta(bfo, tag="6531_a", name="citation_keywords") -}}
{{- bfe_meta(bfo, tag="037__a", name="citation_technical_report_number") -}}
{{- bfe_meta(bfo, tag="088__9", name="citation_technical_report_institution") -}}
{{- bfe_meta(bfo, tag="088__a", name="citation_technical_report_number") -}}
{{- bfe_meta(bfo, tag="020%_a", name="citation_isbn") -}}
{{- bfe_meta(bfo, tag="502__c", name="citation_dissertation_institution") -}}
<meta content="{{ bfe_record_url(bfo, with_ln='no', absolute='yes') }}" name="citation_abstract_html_url" />
{%- if zenodo_files -%}
{%- for file in zenodo_files|sort(attribute='comment') -%}
<link rel="alternate" type="{{file.mime}}" href="{{file.get_url().decode('utf8')}}">
{%- if file.get_superformat() == '.pdf' -%}<meta content="{{file.get_url().decode('utf8')}}" name="citation_pdf_url" />{%- endif -%}
{%- endfor -%}
{%- endif -%}
{%- set icon_url = bfe_icon(bfo, subformat_re='icon-90', as_url=True) -%}
<meta name="twitter:card" content="summary">
<meta name="twitter:site" content="@zenodo_org">
{{- bfe_meta(bfo, tag="245__a", tag_name="title", name="og:title", protocol="opengraph") -}}
{{- bfe_meta(bfo, tag="520__a", tag_name="abstract", name="og:description", protocol="opengraph") -}}
{{- bfe_meta(bfo, var="recurl", name="og:url", protocol="opengraph") -}}
{% if icon_url %}<meta name="og:image" content="{{icon_url}}">{% endif %}
{{- bfe_meta(bfo, var="CFG_SITE_NAME", name="og:site_name", protocol="opengraph") -}}