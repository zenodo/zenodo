{% from "communities/helpers.html" import curation_buttons with context %}
<div class="media htmlbrief">
    <span class="pull-left hidden-phone">
        {{ bfe_icon(bfo, subformat_re='icon-90') }}
    </span>
    <div class="media-body">
        {%- set ucoll_id = collection|community_id %}
        {{ curation_buttons(bfo, ucoll_id) }}
        <span class="label label-info" data-toggle="tooltip" title="Publication date">{{ bfe_date(bfo, date_format='%d %B %Y') }}</span>
        {{ bfe_openaire_pubtype(bfo, as_label="1") }}
        {{ bfe_openaire_access_rights(bfo, as_label="1") }}
        <br/>
        <h4 class="media-heading muted_a"><a href="{{ bfe_record_url(bfo, ) }}">{{ bfe_title_brief(bfo, highlight="no") }}</a></h4>
        <p>{{ bfe_authors(bfo, limit="4", extension="; <em> et al</em> ", highlight="no") }}</p>
        <p class="muted_a"><a href="{{ bfe_record_url(bfo, ) }}">{{ bfo.field('520__a').decode('utf8')|striptags|truncate }}</a></p>
        {% if bfo.field('8560_y') %}<small class="muted">Uploaded by <a href="{{ url_for('yourmessages.write', sent_to_user_nicks=bfo.field('8560_y')) }}">{{bfo.field('8560_y').decode('utf8')}}</a> on {{ bfe_creation_date(bfo, date_format="%d %M %Y") }}.</small>{% endif %}
    </div>
</div>