#!/usr/bin/env bash
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

# First install all node modules
CWD=`pwd`
zenodo npm
cd ${VIRTUAL_ENV}/var/instance/static
npm install

# Symlink to source directories
cd node_modules
rm -Rf invenio-search-js
ln -s ~/src/invenio-search-js invenio-search-js
rm -Rf invenio-records-js
ln -s ~/src/invenio-records-js invenio-records-js
rm -Rf invenio-files-js
ln -s ~/src/invenio-files-js invenio-files-js

# Make sure they are built
cd ~/src/invenio-search-js
npm install
npm run-script build
cd ~/src/invenio-records-js
npm install
npm run-script build
cd ~/src/invenio-files-js
npm install
npm run-script build

# Build assets
cd ${CWD}
zenodo collect -v
zenodo assets build
