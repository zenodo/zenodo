{% from "helpers.html" import copy_to_clipboard -%}
<h1>MARC Export {{copy_to_clipboard(clipboard_target='clipboard_text')}}</h1>
<pre id="clipboard_text">{{ tfn_get_fieldvalues_alephseq_like(recid, [], current_user.get('precached_canseehiddenmarctags', False))|safe }}</pre>