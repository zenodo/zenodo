{#
# This file is part of Zenodo.
# Copyright (C) 2012, 2013, 2014, 2015 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.
#}

{% from "helpers.html" import copy_to_clipboard -%}
<h1>{{record.title}}</h1>
<br>
<h2>BibTeX Export
{{copy_to_clipboard(clipboard_target='clipboard_text')}}
<a class="btn btn-default btn-xs" href="{{url_for('record.metadata', recid=recid)}}"><i class="fa fa-file-text fa-fw"></i> View record</a>
</h2>
<pre id="clipboard_text">{{ record|bibtex }}</pre>
