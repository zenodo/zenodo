// This file is part of Zenodo.
// Copyright (C) 2015, 2016 CERN.
//
// Zenodo is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License as
// published by the Free Software Foundation; either version 2 of the
// License, or (at your option) any later version.
//
// Zenodo is distributed in the hope that it will be
// useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Zenodo; if not, write to the
// Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
// MA 02111-1307, USA.
//
// In applying this license, CERN does not
// waive the privileges and immunities granted to it by virtue of its status
// as an Intergovernmental Organization or submit itself to any jurisdiction.
require([
  "jquery",
  "clipboard",
  "bootstrap",
  "typeahead",
  "bloodhound",
  "node_modules/angular/angular",
  "node_modules/angular-sanitize/angular-sanitize",
  "node_modules/angular-loading-bar/build/loading-bar",
  "node_modules/invenio-csl-js/dist/invenio-csl-js",
  "node_modules/bootstrap-switch/dist/js/bootstrap-switch",
  "js/zenodo/module",
  "js/zenodo/functions",
  "js/github/view",
  ], function($, Clipboard, recordCommunityCurate) {
    // On document ready bootstrap angular
    new Clipboard('.btn.clip-button');
  }
);
