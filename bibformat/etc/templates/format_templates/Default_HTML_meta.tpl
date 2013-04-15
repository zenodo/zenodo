<!-- GoogleScholar -->
{{ bfe_meta(bfo, tag="245__a", name="citation_title") }}
{{ bfe_meta(bfo, tag="100__a", tag_name="first author", name="citation_author") }}
{{ bfe_meta(bfo, tag="700__a", tag_name="additional author", name="citation_author") }}
{{ bfe_meta(bfo, tag="260__b", name="citation_publisher") }}
{{ bfe_meta(bfo, tag="773__a", tag_name="doi", name="citation_doi") }}
{{ bfe_meta(bfo, tag="773__p", tag_name="journal title", name="citation_journal_title") }}
{{ bfe_meta(bfo, tag="773__v", tag_name="journal volume", name="citation_volume") }}
{{ bfe_meta(bfo, tag="773__c", tag_name="journal page", name="citation_firstpage") }}
{{ bfe_meta(bfo, tag_name="journal lastpage", name="citation_lastpage") }}
{{ bfe_meta(bfo, tag="773__i", tag_name="journal issue", name="citation_issue") }}
{{ bfe_meta(bfo, tag="773__t", name="citation_conference") }}
{{ bfe_meta(bfo, tag_name="abstract url", tag="8564_a", name="citation_abstract_url") }}
{{ bfe_meta(bfo, tag_name="date", tag="269__c", name="citation_date") }}
{{ bfe_meta(bfo, tag="695__a", name="citation_keywords") }}
{{ bfe_meta(bfo, tag="037__a", name="citation_technical_report_number") }}
{{ bfe_meta(bfo, tag="088__9", name="citation_technical_report_institution") }}
{{ bfe_meta(bfo, tag="088__a", name="citation_technical_report_number") }}
{{ bfe_meta(bfo, tag="020%_a", name="citation_isbn") }}

<!-- OpenGraph -->
{{ bfe_meta(bfo, tag="245__a", tag_name="title", name="og:title", protocol="opengraph") }}
{{ bfe_meta(bfo, tag="980__a", tag_name="collection", name="og:type", kb="DBCOLLID2OPENGRAPHTYPE", kb_default_output="website", protocol="opengraph") }}
{{ bfe_meta(bfo, var="recurl", name="og:url", protocol="opengraph") }}
{{ bfe_meta_opengraph_video(bfo, ) }}
{{ bfe_meta_opengraph_image(bfo, ) }}
{{ bfe_meta(bfo, var="CFG_SITE_NAME", name="og:site_name", protocol="opengraph") }}
{{ bfe_meta(bfo, tag="520__a", tag_name="abstract", name="og:description", protocol="opengraph") }}