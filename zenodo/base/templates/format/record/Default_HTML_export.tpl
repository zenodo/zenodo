
<div class="well">
    <h4>Export</h4>
    <a href="{{ bfe_server_info(bfo, var='CFG_SITE_URL') }}{{ bfe_server_info(bfo, var='CFG_SITE_RECORD') }}/{{ bfe_record_id(bfo, ) }}/export/hx?ln={{ bfe_client_info(bfo, var='ln') }}">BibTeX</a>,
    <a href="{{ bfe_server_info(bfo, var='CFG_SITE_URL') }}{{ bfe_server_info(bfo, var='CFG_SITE_RECORD') }}/{{ bfe_record_id(bfo, ) }}/export/dcite?ln={{ bfe_client_info(bfo, var='ln') }}">DataCite</a>,
    <a href="{{ bfe_server_info(bfo, var='CFG_SITE_URL') }}{{ bfe_server_info(bfo, var='CFG_SITE_RECORD') }}/{{ bfe_record_id(bfo, ) }}/export/xd?ln={{ bfe_client_info(bfo, var='ln') }}">DC</a>,
    <a href="{{ bfe_server_info(bfo, var='CFG_SITE_URL') }}{{ bfe_server_info(bfo, var='CFG_SITE_RECORD') }}/{{ bfe_record_id(bfo, ) }}/export/xe?ln={{ bfe_client_info(bfo, var='ln') }}">EndNote</a>,
    <a href="{{ bfe_server_info(bfo, var='CFG_SITE_URL') }}{{ bfe_server_info(bfo, var='CFG_SITE_RECORD') }}/{{ bfe_record_id(bfo, ) }}/export/xn?ln={{ bfe_client_info(bfo, var='ln') }}">NLM</a>,
    <a href="{{ bfe_server_info(bfo, var='CFG_SITE_URL') }}{{ bfe_server_info(bfo, var='CFG_SITE_RECORD') }}/{{ bfe_record_id(bfo, ) }}/export/xw?ln={{ bfe_client_info(bfo, var='ln') }}">RefWorks</a></li>
    <a href="{{ bfe_server_info(bfo, var='CFG_SITE_URL') }}{{ bfe_server_info(bfo, var='CFG_SITE_RECORD') }}/{{ bfe_record_id(bfo, ) }}/export/hm?ln={{ bfe_client_info(bfo, var='ln') }}">MARC</a>,
    <a href="{{ bfe_server_info(bfo, var='CFG_SITE_URL') }}{{ bfe_server_info(bfo, var='CFG_SITE_RECORD') }}/{{ bfe_record_id(bfo, ) }}/export/xm?ln={{ bfe_client_info(bfo, var='ln') }}">MARCXML</a>
</div>
