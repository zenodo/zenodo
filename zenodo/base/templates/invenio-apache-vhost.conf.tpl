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
{%- extends "invenio-apache-vhost-zenodo.tpl" -%}

{%- block header -%}
AddDefaultCharset UTF-8
ServerSignature Off
ServerTokens Prod
NameVirtualHost {{ vhost_ip_address }}:{{ vhost_site_url_port }}
{{ '#' if not listen_directive_needed }}{{ 'Listen ' + vhost_site_url_port}}
{{ '#' if not wsgi_socket_directive_needed }}WSGISocketPrefix {{ [config.CFG_PREFIX, 'var', 'run']|path_join }}
{{ super() }}
{%- endblock header -%}
{%- set wsgi_processes = config.get('APACHE_WSGI_DAEMON_PROCESSES', 5) -%}
{%- if config.DEBUG -%}
    {%- set wsgi_processes = 1 -%}
{%- endif -%}
{%- block wsgi %}
        WSGIDaemonProcess invenio processes={{ wsgi_processes }} threads=1 user={{ config.CFG_RUNNING_AS_USER }} display-name=%{GROUP} inactivity-timeout=3600 maximum-requests=10000
        WSGIImportScript {{ config.CFG_WSGIDIR }}/invenio.wsgi process-group=invenio application-group=%{GLOBAL}
        {{ super() }}
{%- endblock wsgi -%}

{%- block auth_shibboleth -%}
{# shibboleth is allowed only on https #}
{%- endblock auth_shibboleth -%}
