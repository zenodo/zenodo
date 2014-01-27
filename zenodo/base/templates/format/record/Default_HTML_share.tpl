<div class="well">
  <span class="pull-right hidden-sm" rel="tooltip" title="QR-code for easy mobile access to this page.">{# bfe_qrcode(bfo, width="100") #}</span>
  <h4>Share </h4>
  <!-- AddThis Button BEGIN -->
<div class="addthis_toolbox addthis_default_style addthis_32x32_style">
<a class="addthis_button_mendeley"></a>
<a class="addthis_button_citeulike"></a>
<a class="addthis_button_twitter"></a>
<a class="addthis_button_preferred_1"></a>
<a class="addthis_button_preferred_2"></a>
<a class="addthis_button_compact"></a>
</div>
<script type="text/javascript">var addthis_config = {"data_track_addressbar":true};</script>
<script type="text/javascript" src="//s7.addthis.com/js/300/addthis_widget.js#pubid=ra-5137aff66ad9c2a1"></script>
<!-- AddThis Button END -->
  <h4>Cite as </h4>
  <p>
  {% set pubinfo = bfe_publi_info(bfo, ) %}
  {{ bfe_authors(bfo, limit="1", extension=" <em>et al</em>", print_links="nanosensors", interactive="no") }} ({{ bfe_year(bfo, ) }}). {{ bfe_title(bfo, ) }}. {{pubinfo if pubinfo else config.CFG_SITE_NAME}}. {{ bfe_doi(bfo, ) }}
  </p>
  <p><small>Further citation formats: <a href="http://crosscite.org/citeproc/">DOI Citation Formatter</a>.</small></p>

</div>