{% from "helpers.html" import copy_to_clipboard -%}
<h1>{{record.title}}</h1>
<br>
<h2>MARC Export {{copy_to_clipboard(clipboard_target='clipboard_text')}}</h2>
<pre id="clipboard_text">{{ tfn_get_fieldvalues_alephseq_like(recid, [], current_user.get('precached_canseehiddenmarctags', False))|safe }}</pre>
