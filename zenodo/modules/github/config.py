# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2014 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

GITHUB_WEBHOOK_RECEIVER_ID = "github"
"""
Local name of webhook receiver.
"""

GITHUB_BASE_URL = "https://api.github.com"
"""
Base URL of the GitHub API
"""

GITHUB_SHARED_SECRET = "CHANGEME"
"""
Shared secret between you and GitHub. Used to make GitHub sign webhook requests
with HMAC.

See http://developer.github.com/v3/repos/hooks/#example
"""

GITHUB_INSECURE_SSL = False
"""
Determines if the GitHub webhook request will check the SSL certificate. Never
set to True in a production environment, but can be useful for development and
integration servers.
"""
