// This file is part of Zenodo.
// Copyright (C) 2018 CERN.
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

 define([], function(){
  function providerNamesFilter() {
    return function(relationship) {
      var providerNames = [];
      for (var linkHistory of relationship.metadata.History) {
        for (var provider of linkHistory.LinkProvider) {
          if (!providerNames.includes(provider.Name)) {
            providerNames.push(provider.Name);
          }
        }
      }
      return providerNames.join(', ');
    };
  }

  function creatorNamesFilter() {
    return function(relationship) {
      var creatorNames = [];
      var creators = relationship.metadata.Target.Creator;
      if (creators) {
        for(var i=0; i<creators.length && i<5; i++) {
          creatorNames.push(creators[i].Name);
        }
        if(creators.length > 5) {
        creatorNames.push("et al.");
        }
      }
      return creatorNames.join(', ');
    };
   }

   function doiUrlFilter() {
     return function(relationship) {
      var doiUrl = "";
      var url = "";
        for(identifier of relationship.metadata.Target.Identifier) {
          if(identifier.IDURL) {
            url = identifier.IDURL;
            if (identifier.IDScheme == "doi") {
              doiUrl = identifier.IDURL;
              break;
            }
          }
        }
      return doiUrl || url;
     };
   }

  return {providerNamesFilter:providerNamesFilter, creatorNamesFilter: creatorNamesFilter, doiUrlFilter: doiUrlFilter};
});


