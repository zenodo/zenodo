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


// Overriding ui-select's controller to handle arrays
//
// Note: UI-Select by default doesn't play well while being inside an
// array. What happens is that if the array gets modified from the
// outside (eg. delete an array element), the changes are not picked up
// by UI-Select, and thus aren't refelcted on its internal model and
// view. This leads to inconsistent view state for the end user, eg.
// an item from the middle of a ui-select list gets removed using the
// 'X' button, but the view will still display it and remove the last
// item of the list.
//
// The remedy for this issue is to handle the update of ui-select's
// model manually, by overriding its controller.
function invenioDynamicSelectController($scope, $controller) {
  $controller('dynamicSelectController', {$scope: $scope});
  // If it is ui-select inside an array...
  if ($scope.modelArray) {
    $scope.$watchCollection('modelArray', function(newValue) {
      // If this is not the initial setting of the element...
      if (!angular.equals($scope.select_model, {})) {
        // Get the element's correct value from the array model
        var value = $scope.modelArray[$scope.arrayIndex][$scope.form.key.slice(-1)[0]];
        // Set ui-select's model to the correct value if needed
        if ($scope.insideModel !== value) {
          $scope.insideModel = value;
          var query = $scope.$eval(
            $scope.form.options.processQuery || 'query',
            { query: value }
          );
          $scope.populateTitleMap($scope.form, query);
          $scope.select_model.selected = $scope.find_in_titleMap(value);
        }
      }
    });
  }
}

invenioDynamicSelectController.$inject = [
  '$scope',
  '$controller',
];

angular.module('schemaForm')
  .controller('invenioDynamicSelectController', invenioDynamicSelectController);
