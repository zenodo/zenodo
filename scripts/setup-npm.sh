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

# This is to fix bug https://github.com/zenodo/zenodo/issues/2154. This script
# fails because npm is not installed. So let's install npm first.
curl https://nodejs.org/download/release/v7.4.0/node-v7.4.0-linux-x64.tar.gz -o node-v7.4.0-linux-x64.tar.gz
gunzip node-v7.4.0-linux-x64.tar.gz
tar xvf node-v7.4.0-linux-x64.tar --strip-components=1 -C /usr/local
# end of fix

# Checking node version
node_version="$(node --version)"
if [[ -z "$node_version" ]]
then
    echo "Node is not installed"
elif [[ ! $node_version = *v7* ]] && [[ ! $node_version = *v6* ]]
then
    echo >&2 "Sorry, you are using node version $node_version, which is incompatible. Please install node 7.4.0"; exit 1;
fi

npm update && npm install --silent -g node-sass@3.8.0 clean-css@3.4.19 uglify-js@2.7.3 requirejs@2.2.0
