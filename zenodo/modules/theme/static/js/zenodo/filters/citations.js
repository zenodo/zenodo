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

define([], function() {
  function providerNamesFilter() {
    return function(relationship) {
      var providerNames = [];
      relationship.metadata.History.forEach(function(linkHistory) {
        linkHistory.LinkProvider.forEach(function(provider) {
          if (!providerNames.includes(provider.Name)) {
            providerNames.push(provider.Name);
          }
        });
      });
      return providerNames.join(', ');
    };
  }

  function creatorNamesFilter() {
    return function(relationship) {
      var creatorNames = "";
      var creators = relationship.metadata.Source.Creator;
      if (creators) {
        creatorNames = creators[0].Name;
        if (creators.length == 2) {
          creatorNames = creatorNames + " & " + creators[1].Name;
        }
        else if (creators.length > 2) {
          creatorNames = creatorNames + " et al.";
        }
      }
      return creatorNames;
    };
  }

  function doiUrlFilter() {
    return function(relationship) {
      var doiUrl = "";
      var url = "";

      relationship.metadata.Source.Identifier.forEach(function(identifier) {
        if (identifier.IDURL) {
          url = identifier.IDURL;
          if (identifier.IDScheme == "doi") {
            doiUrl = identifier.IDURL;
          }
        }
      });

      return doiUrl || url;
    };
  }

  function doiFilter() {
    return function(relationship) {
      var doi = "";
      if(relationship.metadata.Source.Identifier) {
        relationship.metadata.Source.Identifier.forEach( function(identifier) {
          if (identifier.ID && identifier.IDScheme == "doi") {
              doi = identifier.ID;
          }
        });
      }
      return doi;
    };
  }

  function citationTitleFilter() {
    return function(relationship) {
      var title = relationship.metadata.Source.Title;
      if (!title || title.length === 0) {
        // Use the first identifier or the DOI
        relationship.metadata.Source.Identifier.forEach(function(identifier) {
          if (identifier.IDURL) {
            title = identifier.IDScheme.toUpperCase() + ': ' + identifier.ID;
            if (identifier.IDScheme == 'doi') {
              title = 'DOI: ' + identifier.ID;
            }
          }
        })
      }
      return title;
    };
  }

  function logoTypeFilter() {
    return function(relationship) {
      var logoType = {
        "literature": "fa-file-text",
        "dataset": "fa-table",
        "software": "fa-code",
        "unknown": "fa-asterisk"
      };
      var logo = "fa-asterisk";
      if (relationship.metadata.Source.Type) {
        logo = logoType[relationship.metadata.Source.Type.Name] || "fa-asterisk";
      }
      return logo;
    };
  }

  function uniqueBadgeFilter() {
    return function (identifiers) {
      schemes = [];
      uniqueIdentifiers = [];
      if (identifiers) {
        identifiers.forEach(function (identifier) {
          if (identifier.IDURL && !schemes.includes(identifier.IDScheme)) {
            uniqueIdentifiers.push(identifier)
            schemes.push(identifier.IDScheme);
          }
        });
      }
      return uniqueIdentifiers;
    };
  }

  function missingTypesFilter() {
    return function(buckets) {
      var missingTypes = ["literature", "dataset", "software", "unknown"];
      if(buckets) {
        buckets.forEach(function(bucket) {
          missingTypes.splice(missingTypes.indexOf(bucket.key), 1);
        });
      }

      return missingTypes;
    };
  }

  return {
    providerNamesFilter: providerNamesFilter,
    creatorNamesFilter: creatorNamesFilter,
    doiUrlFilter: doiUrlFilter,
    doiFilter: doiFilter,
    citationTitleFilter: citationTitleFilter,
    logoTypeFilter: logoTypeFilter,
    uniqueBadgeFilter: uniqueBadgeFilter,
    missingTypesFilter: missingTypesFilter,
  };
});
