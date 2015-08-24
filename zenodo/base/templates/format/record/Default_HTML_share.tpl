{#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software; you can redistribute it and/or modify
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

{% from "citationformatter/macros.html" import citationformatter %}
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
<script type="text/javascript">
var addthis_config = {
  "data_track_addressbar": true
};
var addthis_share = {
  url: "http://dx.doi.org/{{record.doi}}"
};
</script>
<script type="text/javascript" src="//s7.addthis.com/js/300/addthis_widget.js#pubid=ra-5137aff66ad9c2a1"></script>
<!-- AddThis Button END -->
{% if record.doi %}
  <h4>Cite as </h4>
  {{ citationformatter(record.doi, bfe_authors(bfo, limit="1", extension=" et al.", print_links="nanosensors", interactive="no") + '. (' + bfe_year(bfo, ) +'). ' + bfe_title(bfo, ) + '. ' + (pubinfo if pubinfo else config.CFG_SITE_NAME) + '. ' + bfe_doi(bfo, )) }}
{% endif %}
</div>
