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

define([], function () {
  function providerNamesFilter() {
    return function (relationship) {
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
    return function (relationship) {
      var creatorNames = [];
      var creators = relationship.metadata.Source.Creator;
      if (creators) {
        for (var i = 0; i < creators.length && i < 5; i++) {
          creatorNames.push(creators[i].Name);
        }
        if (creators.length > 5) {
          creatorNames.push("et al.");
        }
      }
      return creatorNames.join('; ');
    };
  }

  // Modify to return both DOI_URL and DOI
  function doiUrlFilter() {
    return function (relationship) {
      var doiUrl = "";
      var url = "";
      for (identifier of relationship.metadata.Source.Identifier) { // Modify to foreach
        if (identifier.IDURL) {
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

  // function doiIdentifierFilter() {
  //   return function (relationship) {
  //     var doi_identifier_object = null;
  //     var default_identifier_object = null;
  //     relationship.metadata.Source.Identifier.forEach(function(identifier) {
  //       if (identifier.IDURL) {
  //         default_identifier_object = identifier;
  //         if (identifier.IDScheme == "doi") {
  //           doi_identifier_object = identifier;
  //         }
  //       }
  //     })
  //     return doi_identifier_object || default_identifier_object;
  //   };
  // }

  function identifierColorFilter() {
    return function (identifier) {
      var typeID = {
        "doi": function () {
          return "label-info";
        },
        "arxiv": function () {
          return "label-danger";
        },
        "ads": function () {
          return "label-default";
        },
        "default": function () {
          return "label-success";
        }
      };
      return (typeID[identifier.IDScheme] || typeID['default'])();
    };
  }

  function logoTypeFilter() {
    return function (relationship) {
      return {
        "literature": "fa-file-text",
        "dataset": "fa-table",
        "software": "fa-code",
        "unknown": "fa-asterisk"
      }[relationship.metadata.Source.Type.Name] || "fa-asterisk";
    };
  }
  return { providerNamesFilter: providerNamesFilter, creatorNamesFilter: creatorNamesFilter, doiUrlFilter: doiUrlFilter, identifierColorFilter: identifierColorFilter, logoTypeFilter: logoTypeFilter };
});
