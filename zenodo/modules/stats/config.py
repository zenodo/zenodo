# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Configuration for Zenodo stats."""

ZENODO_STATS_PIWIK_EXPORTER = {
    'id_site': 1,
    'url': 'https://analytics.openaire.eu/piwik.php',
    'token_auth': 'api-token',
    'chunk_size': 50  # [max piwik payload size = 64k] / [max querystring size = 750]
}

# max querystring size:
# idsite=17 		        # 6+2=8
# rec=1			            # 3+1=4
# url=<url>			        # 3+41(file URL)+252(max file name)=296
#                           (x2 in case of file download)
# _id=<visitor_id>          # 3+57=60
# cid=<visitor_id>	        # 3+57=60
# cvar=<cvar>		        # 4+150=154
# cdt=event.timestamp	    # 3+20=23
# urlref=event.referrer	    # 6+150=156
# action_name=action_name	# 11+150=161
#
# \ -> 30
# & -> 9
# ? -> 1
# = -> 10
#
# tot: 1268

ZENODO_STATS_PIWIK_EXPORT_ENABLED = True

# Queries performed when processing aggregations might take more time than
# usual. This is fine though, since this is happening during Celery tasks.
ZENODO_STATS_ELASTICSEARCH_CLIENT_CONFIG = {'timeout': 60}

ZENODO_STATS_DATACITE_API_URL = 'https://api.test.datacite.org/reports/'
"""DataCite usage statistics reports endpoint."""

ZENODO_STATS_DATACITE_TOKEN = None
"""DataCite usage statistics API token."""

ZENODO_STATS_DATACITE_REPORT_MAX_ITEMS = 50000
"""Max items to send per report."""

ZENODO_STATS_DATACITE_REPORT_HEADER = {
    'created-by': 'Zenodo',
    'report-name': 'dataset report',
    'report-id': 'DSR',
    'release': 'rd1',
}
"""DataCite usage statistics report header fields."""

ZENODO_STATS_LOCAL_PUBLISHER = {
    'name': 'Zenodo',
    'grid': 'grid.9132.9',  # CERN GRID identifier
}
"""Publisher information for DataCite statistics report."""

ZENODO_STATS_DOI_PREFIX_PUBLISHERS = {}
"""Mapping between DOI prefixes and publisher information.

Used in DataCite statistics report for foreign DOIs. Example config:

..code-block:: python

    ZENODO_STATS_DOI_PREFIX_PUBLISHERS = {
        '10.1234': {
            'name': 'Foo publisher',  # required
            # at least one of "grid", "isni", "urn", "orcid" is required
            'grid': 'grid.12345.6',
            'isni': '000000012146438X',
        },
    }
"""
