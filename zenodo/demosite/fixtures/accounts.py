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


from fixture import DataSet
from invenio.config import CFG_SITE_ADMIN_EMAIL


class UserData(DataSet):
    class admin:
        id = 1
        email = CFG_SITE_ADMIN_EMAIL
        password = ''
        note = '1'
        nickname = 'admin'

    class info:
        id = 2
        email = 'info@zenodo.org'
        password = 'info'
        note = '1'
        nickname = 'info'

    class usera:
        id = 3
        email = 'user.a@zenodo.org'
        password = 'usera'
        note = '1'
        nickname = 'usera'

    class userb:
        id = 4
        email = 'user.b@zenodo.org'
        password = 'userb'
        note = '1'
        nickname = 'userb'

    class user_inactive:
        id = 5
        email = 'inactive@zenodo.org'
        password = 'inactive'
        note = '2'  # Email confirm required
        nickname = 'inactive'

    class user_blocked:
        id = 6
        email = 'blocked@zenodo.org'
        password = 'blocked'
        note = '0'  # Administrator approval required
        nickname = 'blocked'
