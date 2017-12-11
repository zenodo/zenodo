// This file is part of Zenodo.
// Copyright (C) 2017 CERN.
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

function configZenodoDeposit($provide, decoratorsProvider) {

  // TODO: Check if these are needed, since we have DEPOSIT_FORM_TEMPLATES
  // New field types
  decoratorsProvider.addMapping('bootstrapDecorator', 'uiselect', '/static/templates/zenodo_deposit/uiselect.html');
  decoratorsProvider.addMapping('bootstrapDecorator', 'ckeditor', '/static/templates/zenodo_deposit/ckeditor.html');
  decoratorsProvider.defineAddOn(
    'bootstrapDecorator',
    'grantselect',
    '/static/templates/zenodo_deposit/grantselect.html")}}'
  );
  decoratorsProvider.defineAddOn(
    'bootstrapDecorator',
    'communities',
    '/static/templates/zenodo_deposit/communities.html'
  );

  // Override invenio-records-form
  $provide.decorator('invenioRecordsFormDirective', function($delegate) {
    var directive = $delegate[0];
    var link = directive.link;
    directive.compile = function() {
      return function Link(scope, element, attrs, ctrls) {
        scope.autocompleteGrants = function(options, query) {
          // Autocomplete is triggered either from user input or change
          // of state in the model (form initialization, internal
          // modifications, etc)
          var isUserSearch = query !== '' && query !== options.scope.insideModel;
          if (query === '' && !isUserSearch) {
            query = options.scope.insideModel || '';
          }

          var query_parts = query.split('::');
          query = query_parts.pop()
          var funder = isUserSearch ?
            options.scope.funder.value
            : options.scope.form.default_funder;
          // Handle legacy FP7 grant values (only "grant_id")
          if (query_parts.length === 1) {
            funder = query_parts.pop();
          }
          options.scope.funder = {value: funder};
          options.urlParameters.funder = "'" + funder + "'";
          return scope.autocompleteSuggest(options, query)
        }

        return link.apply(this, arguments);
      };
    };
    return $delegate;
  });
}

configZenodoDeposit.$inject = [
  '$provide',
  'schemaFormDecoratorsProvider',
];

angular.module('invenioRecords')
  .config(configZenodoDeposit);
