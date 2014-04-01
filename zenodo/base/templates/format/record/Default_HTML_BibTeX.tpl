{% from "helpers.html" import copy_to_clipboard -%}
<h1>BibTeX Export {{copy_to_clipboard(clipboard_target='clipboard_text')}}</h1>
<pre id="clipboard_text">{{ bfe_bibtex(bfo, width="80") }}</pre>
