#!/usr/bin/env bash
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
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

if [ -d "$VIRTUAL_ENV/var/instance/data" ]; then
    rm -Rf $VIRTUAL_ENV/var/instance/data
fi

zenodo db destroy --yes-i-know
zenodo db init
zenodo db create
zenodo index destroy --force --yes-i-know
zenodo index queue init
zenodo index init
zenodo fixtures init
zenodo fixtures loadlicenses
zenodo fixtures loadfp6funders
zenodo fixtures loadfp6grants
zenodo users create info@zenodo.org -a --password=123456
zenodo access allow admin-access -e info@zenodo.org
zenodo access allow deposit-admin-access -e info@zenodo.org
zenodo fixtures loadcommunities info@zenodo.org
