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

function prereserveButton($rootScope, InvenioRecordsAPI) {
  function link($scope, elem, attrs, vm) {
    $scope.prereserveDOI = function() {
      if ($scope.model.prereserve_doi &&
          $scope.model.prereserve_doi.doi) {
        $scope.model.doi = $scope.model.prereserve_doi.doi;
      } else {
        // We need to make a 'POST' call to create a deposit, or a
        // 'GET' in case we already have one, in order to get the
        // pre-reserved DOI.
        var method = angular.isUndefined(vm.invenioRecordsEndpoints.self) ? 'POST': 'GET';
        var url = vm.invenioRecordsEndpoints.self || vm.invenioRecordsEndpoints.initialization;
        $rootScope.$broadcast('invenio.records.loading.start');
        InvenioRecordsAPI.request({
          method: method,
          url: url,
          data: {},
          headers: vm.invenioRecordsArgs.headers || {}
        }).then(function success(resp) {
          if (resp.data.metadata &&
              resp.data.metadata.prereserve_doi &&
              resp.data.metadata.prereserve_doi.doi) {
            $scope.model.prereserve_doi = resp.data.metadata.prereserve_doi;
            $scope.model.doi = resp.data.metadata.prereserve_doi.doi;
          }
          $rootScope.$broadcast(
            'invenio.records.endpoints.updated', resp.data.links);
        }, function error(resp) {
          $rootScope.$broadcast('invenio.records.alert', {
            type: 'danger',
            data: resp.data,
          });
        })
        .finally(function() {
          $rootScope.$broadcast('invenio.records.loading.stop');
        });
      }
    };
  }

  return {
    scope: false,
    restrict: 'A',
    require: '^invenioRecords',
    link: link,
  };
}

prereserveButton.$inject = [
  '$rootScope',
  'InvenioRecordsAPI',
];

angular.module('invenioRecords.directives')
  .directive('prereserveButton', prereserveButton)
