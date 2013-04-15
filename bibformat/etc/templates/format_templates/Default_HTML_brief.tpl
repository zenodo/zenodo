
<div class="media htmlbrief">
    <span class="pull-left hidden-phone">
        {{ bfe_icon(bfo, subformat_re='icon-90') }}
    </span>
    <span class="pull-right hidden-phone">
        {{ bfe_openaire_altmetric(bfo, badgetype='donut', popover='left', no_script='1', prefix="<br>") }}
    </span>
    <div class="media-body">
        <span class="label label-info">{{ bfe_creation_date(bfo, date_format="%d %M %Y") }}</span>
        {{ bfe_openaire_pubtype(bfo, as_label="1") }}
        {{ bfe_openaire_access_rights(bfo, as_label="1") }}
        <br/>
        <h4 class="media-heading muted_a"><a href="{{ bfe_record_url(bfo, ) }}">{{ bfe_title_brief(bfo, highlight="no") }}</a></h4>
        <p>{{ bfe_authors(bfo, limit="4", extension="; <em> et al</em> ", highlight="no") }}</p>
        <p class="muted_a"><a href="{{ bfe_record_url(bfo, ) }}">{{ bfe_abstract(bfo, limit="1", highlight="no", contextual="no") }}</a></p>
    </div>
</div>