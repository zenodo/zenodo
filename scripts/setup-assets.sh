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

set -e

CWD=`pwd`
SOURCE=${1:-"package.pinned.json"}

# Checking node version
node_version="$(node --version)"
if [[ -z "$node_version" ]]
then
    echo "Node is not installed"
elif [[ ! $node_version = *v7* ]] && [[ ! $node_version = *v6* ]]
then
    echo >&2 "Sorry, you are using node version $node_version, which is incompatible. Please install node 7.4.0"; exit 1;
fi

# Checking binaries
if [[ -z "$(which cleancss)" || -z "$(which node-sass)" || -z "$(which uglifyjs)" || -z "$(which r_js)" ]]
then
    echo "Please run ./setup-npm"; exit 1;
fi

zenodo npm --pinned-file ${SOURCE}
cd ${VIRTUAL_ENV}/var/instance/static
rm -rf gen .webassets-cache
npm install
cd ${CWD}
zenodo collect -v
zenodo assets build
