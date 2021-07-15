# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2017-2021 CERN.
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

"""Test Zenodo metrics views."""
from flask import Response


def test_metrics(app, db, es, use_metrics_config):
    expected_data = '# HELP zenodo_unique_visitors_web_total Number ' \
                    'of unique visitors in total on Zenodo portal\n' \
                    '# TYPE zenodo_unique_visitors_web_total gauge\n' \
                    'zenodo_unique_visitors_web_total 0\n' \
                    '# HELP zenodo_researchers_total Number of ' \
                    'researchers registered on Zenodo\n' \
                    '# TYPE zenodo_researchers_total gauge\n' \
                    'zenodo_researchers_total 0\n' \
                    '# HELP zenodo_files_total Number of files hosted ' \
                    'on Zenodo\n' \
                    '# TYPE zenodo_files_total gauge\n' \
                    'zenodo_files_total 0\n' \
                    '# HELP zenodo_communities_total Number of Zenodo ' \
                    'communities created\n' \
                    '# TYPE zenodo_communities_total gauge\n' \
                    'zenodo_communities_total 0\n' \

    with app.test_client() as client:
        res = client.get("/api/metrics/openaire-nexus")
        assert res.status_code == 200
        assert res.get_data() == expected_data


def test_metrics_invalid_key(app):
    with app.test_client() as client:
        res = client.get("/api/metrics/invalid-key")
        assert res.status_code == 404
        assert res.get_data() == 'Invalid key'
