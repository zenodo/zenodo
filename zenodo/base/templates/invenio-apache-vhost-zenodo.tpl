{#
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#}

{%- extends "invenio-apache-vhost.tpl" -%}

{%- block aliases %}
{{ super() }}
        Alias /font/ /home/lnielsen/envs/zenodomaster/var/www/font/
{%- endblock -%}

{%- block xsendfile_directive %}
    {{ super() }}
    {%- if config.CFG_BIBDOCFILE_USE_XSENDFILE and config.DEBUG %}
        XSendFilePath {{ [config.CFG_PREFIX, 'lib', 'python2.7', 'site-packages', 'flask_debugtoolbar', 'static']|path_join }}
        XSendFilePath {{ [config.CFG_PREFIX, 'local', 'lib', 'python2.7', 'site-packages', 'flask_admin', 'static']|path_join }}
    {%- endif -%}
{%- endblock xsendfile_directive -%}