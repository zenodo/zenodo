{% from "communities/helpers.html" import curation_buttons with context %}
{% for coll in bfo|communities(provisional=True, public=False, is_owner=True) %}
{% if loop.first %}
<h5><i class="fa fa-legal"></i> <strong>Pending approvals</strong></h5>
<div class="cycle-well-row">
{% endif %}
<div class="row"><div class="col-md-12">
    {{ curation_buttons(bfo, coll.id, btnsize='btn-xs') }}
    {{coll.title}}
</div></div>
{% if loop.last %}</div>{% endif %}
{% endfor %}

{% for coll in bfo|communities(provisional=False, public=True, is_owner=True) %}
{% if loop.first %}
<h5><i class="fa fa-check"></i> <strong>Existing approvals</strong></h5>
<div class="cycle-well-row">
{% endif %}
<div class="row"><div class="col-md-12">
    {{ curation_buttons(bfo, coll.id, btnsize='btn-xs', show_state=False) }}
    {{coll.title}}
</div></div>
{% if loop.last %}</div>{% endif %}
{% endfor %}

{# Record owner is allowed to remove his record from a given collection #}
{% if bfo|is_record_owner %}
    {% for coll in bfo|communities(public=True, is_owner=False, exclude=[
            'user-zenodo', 'provisional-user-zenodo']) %}
        {% if loop.first %}
            <h5><i class="fa fa-group"></i> <strong>Communities</strong></h5>
            <div class="cycle-well-row">
        {% endif %}
        <div class="row"><div class="col-md-12">
            {{ curation_buttons(bfo, coll.id, btnsize='btn-xs', type='remove', show_state=False) }}
            {{coll.title}}
        </div></div>
        {% if loop.last %}
        </div>
        <small class="text-muted">Your upload is included in above community collections. Click the remove button, to remove your upload from the community collection (cannot be undone!).</small>
        {% endif %}
    {% endfor %}
{% endif %}
