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

function fieldtitle() {
  return function(fieldname, schemaform) {
    if (!fieldname){
      return null;
    }
    var parts = fieldname.split('.');
    parts.shift(); // pop metadata
    var title = null;
    for (var i = 0; i < schemaform.length && parts.length != 0; i++) {
      var set = schemaform[i];
      for (var j = 0; j < set.items.length && parts.length != 0; j++) {
        var field = set.items[j];
        if(field && field.type != "section" && field.key && field.key[0] == parts[0] ){
          if(field.title) {
              title = field.title;
          }
          parts.shift();
        }
      }
    }
    return title;
  };
}

function notIn($filter) {
  return function(srcArray, filterArray, srcKey, filterKey){
    if(srcArray && srcArray.length && filterArray && filterArray.length){
      return $filter('filter')(srcArray, function(srcItem){
        return !filterArray.some(function(filterItem) {
          srcValue = srcKey ? srcItem[srcKey] : srcItem;
          filterValue = filterKey ? filterItem[filterKey] : filterItem;
          return srcValue === filterValue;
        });
      });
    }
    return srcArray;
  };
}


function formatGrant() {
  return function (grant) {
    if (!grant) {
      return '';
    }
    var result = (grant.acronym && grant.acronym + ' ') || '';
    return result + '(' + grant.code + ') - ' + grant.title;
  };
}


function striptags() {
  return function(text) {
    return text ? String(text).replace(/<[^>]+>/gm, '') : '';
  };
}


function limitToEllipsis() {
  return function(text, n) {
    return (text.length > n) ? text.substr(0, n-1) + '&hellip;' : text;
  };
}

// Bestowed upon us by https://github.com/angular/angular.js/issues/15874#issuecomment-290662445
function stable() {
  var valueCache = {};
  return function(value, key) {
    valueCache[key] = angular.equals(value, valueCache[key]) ? valueCache[key] : value;
    return valueCache[key];
  };
}

function checkAllFilesUploaded() {
  return function(file_objects) {
    var incompleted_uploads= false;
    angular.forEach(file_objects, function(file_object) {
      if (typeof file_object.completed == "undefined" || file_object.completed !== true) {
        incompleted_uploads = true;
      }
    });
    return incompleted_uploads;
 };
}

function formatOpenAIRECommunities() {
  return function (comm_ids, oa_comms) {
    result = '';
    if (comm_ids) {
      result = [];
      angular.forEach(comm_ids, function(comm_id) {
        oa_comm = oa_comms[comm_id].name
        result.push(oa_comm)
      });
      result = result.join(', ') + '.';
    }
    return result;
  };
}

function fileSizeFormat() {

  function filter(size) {
    function round(num, precision) {
      return Math.round(
        num * Math.pow(10, precision)) / Math.pow(10, precision
      );
    }
    var limit = Math.pow(1000, 4);
    if (size > limit) {
      return round(size / limit, 1) + ' TB';
    } else if (size > (limit/=1000)) {
      return round(size / limit, 1) + ' GB';
    } else if (size > (limit/=1000)) {
      return round(size / limit, 1) + ' MB';
    } else if (size > 1000) {
      return Math.round(size / 1000) +  ' kB';
    }
    if (size === 1) {
      return "1 Byte"
    }
    return size + ' Bytes';
  }

  ////////////

  return filter;
}


angular.module('invenioRecords')
  .filter('fieldtitle', fieldtitle)
  .filter('notIn', notIn)
  .filter('formatGrant', formatGrant)
  .filter('limitToEllipsis', limitToEllipsis)
  .filter('striptags', striptags)
  .filter('stable', stable)
  .filter('checkAllFilesUploaded',checkAllFilesUploaded)
  .filter('formatOpenAIRECommunities', formatOpenAIRECommunities)
  .filter('fileSizeFormat', fileSizeFormat);
