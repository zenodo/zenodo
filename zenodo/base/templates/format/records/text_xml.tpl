<?xml version="1.0" encoding="UTF-8"?>
{%- for recid in recids -%}
{{ format_record(recid, of=of)|indent() }}
{%- endfor %}