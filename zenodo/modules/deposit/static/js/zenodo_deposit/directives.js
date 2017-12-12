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


function communitiesSelect($http, $q, openAIRE) {
  function link($scope, elem, attrs, vm) {
    // Locals
    function initCommunities() {
      $scope.model.communities = $scope.model.communities || [];
      $scope.model.communities = $scope.model.communities.filter(
        function(comm) { return 'identifier' in comm; });
      var requests = $scope.model.communities.filter(function(comm) {
        return 'identifier' in comm;
      }).map(function(comm) {
        return $http.get('/api/communities/' + comm.identifier);
      });
      // TODO: Add a loading indicator
      $q.all(requests).then(function(fetchedCommunities) {
        $scope.communities = fetchedCommunities.map(function(res) {
          return res.data;
        }).filter(function(comm) { return 'id' in comm; });
      });
    }

    $scope.communities = [];
    $scope.communityResults = [];
    $scope.openAIRECommunities = openAIRE.communities;
    $scope.openAIRECommunitiesMapping = openAIRE.communitiesMapping;

    initCommunities();

    // Methods
    $scope.refreshCommunityResults = function(data) {
      var data = data || $scope.communityResults;
      $scope.communityResults = _.filter(data, function(comm){
        return _.find($scope.communities, function(c) { return c.id == comm.id}) == undefined;
      });
    };

    $scope.searchCommunities = function(query) {
      $http.get('/api/communities', {params: {q: query, size: 7} })
      .then(function(res){
        $scope.refreshCommunityResults(res.data.hits.hits);
      });
    }

    $scope.communityOnSelect = function(community) {
      $scope.communities.push(community)
      $scope.model.communities.push({identifier: community.id})
      $scope.refreshCommunityResults()
    };

    $scope.removeCommunity = function(commId) {
      $scope.communities = _.filter($scope.communities, function(comm){
        return comm.id !== commId;
      });
      $scope.model.communities = _.filter($scope.model.communities, function(comm){
        return comm.identifier !== commId;
      });
      // Unset the OpenAIRE subtype
      $scope.model.openaire_type = undefined;
      $scope.refreshCommunityResults()
    }
  }
  return {
    scope: false,
    restrict: 'AE',
    require: '^invenioRecords',
    link: link,
  };
}

communitiesSelect.$inject = [
  '$http',
  '$q',
  'openAIRE',
];


function openaireSubtype(openAIRE) {
  function link($scope, elem, attrs, vm) {
    // Locals
    $scope.openAIRECommunities = openAIRE.communities;
    $scope.openAIRECommunitiesMapping = openAIRE.communitiesMapping;
    $scope.vm = vm;

    // Methods
    function getOpenAIRECommunities() {
      var modelCommunities = $scope.model.communities || [];
      var openaireComms = [];
      _.each(modelCommunities, function(comm) {
        if (comm.identifier in $scope.openAIRECommunitiesMapping) {
          openaireComms.push($scope.openAIRECommunitiesMapping[comm.identifier]);
        }
      });
      return _.uniq(openaireComms);
    }

    $scope.show = function() {
      var uploadType = $scope.model.upload_type;
      var openaireComms = getOpenAIRECommunities();
      var commTypes = _.pick($scope.openAIRECommunities, openaireComms)
      var res = !angular.equals(commTypes, {}) &&
      _.any(commTypes, function(comm) { return uploadType in comm.types; });
      return res;
    }

    $scope.getOptions = function() {
      var uploadType = $scope.model.upload_type;
      var openaireComms = getOpenAIRECommunities();
      var commTypes = _.pick($scope.openAIRECommunities, openaireComms)
      var options = [];
      _.each(commTypes, function(comm) {
        _.each(comm.types[uploadType] || [], function(type) {
          options.push({ id: type.id, name: type.name, commName: comm.name })
        })
      })
      return options;
    }
  }
  return {
    scope: false,
    restrict: 'AE',
    require: '^invenioRecords',
    link: link,
  };
}

openaireSubtype.$inject = [
  'openAIRE',
];


angular.module('invenioRecords.directives')
  .directive('prereserveButton', prereserveButton)
  .directive('communitiesSelect', communitiesSelect)
  .directive('openaireSubtype', openaireSubtype);
