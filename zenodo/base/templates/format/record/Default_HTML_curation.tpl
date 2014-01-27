{% from "communities/helpers.html" import curation_buttons with context %}
{% for coll in bfo|communities(provisional=True, public=False, is_owner=True) %}
{% if loop.first %}
<h5><i class="icon-legal"></i> Pending approvals</h5>
{% endif %}
<div>
    {{ curation_buttons(bfo, coll.id, btnsize='btn-mini') }}
    {{coll.title}}
</div>
{% if not loop.last %}<hr />{% endif %}
{% endfor %}

{% for coll in bfo|communities(provisional=False, public=True, is_owner=True) %}
{% if loop.first %}
<h5><i class="icon-check"></i> Existing approvals</h5>
{% endif %}
<div>
    {{ curation_buttons(bfo, coll.id, btnsize='btn-mini', show_state=False) }}
    {{coll.title}}
</div>
{% if not loop.last %}<hr />{% endif %}
{% endfor %}

{# Record owner is allowed to remove his record from a given collection #}
{% if bfo|is_record_owner %}
    {% for coll in bfo|communities(public=True, is_owner=False, filter_zenodo=True) %}
        {% if loop.first %}
            <h5><i class="icon-group"></i> Communities</h5>
        {% endif %}
        <div>
            {{ curation_buttons(bfo, coll.id, btnsize='btn-mini', type='remove', show_state=False) }}
            {{coll.title}}
        </div>
        {% if loop.last %}
        <small class="muted">Your upload is included in above community collections. Click the remove button, to remove your upload from the community collection (cannot be undone!).</small>
        {% endif %}
    {% endfor %}
{% endif %}
