{% for recid in recids -%}
{{ format_record(recid, of='dcite')|indent() }}
{%- endfor %}