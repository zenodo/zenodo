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

{% set log_suffix = '-ssl' %}

{%- block header -%}
{{ '#' if not listen_directive_needed }}{{ 'Listen ' + vhost_site_url_port}}
NameVirtualHost {{ vhost_ip_address }}:{{ vhost_site_url_port }}
{%- endblock -%}

{%- block server %}
        {{ super() }}
        SSLEngine on
        SSLCertificateFile {{config.CFG_ETCDIR}}/certs/localhost.crt
        SSLCertificateKeyFile {{config.CFG_ETCDIR}}/certs/localhost.key
{%- endblock server -%}

{%- block wsgi %}
        RedirectMatch /sslredirect/(.*) http://$1
        {{ super() }}
{%- endblock wsgi -%}
