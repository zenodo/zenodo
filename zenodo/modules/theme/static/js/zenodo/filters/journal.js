// This file is part of Zenodo.
// Copyright (C) 2019 CERN.
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

  function formatJournalFilter() {
    return function(record) {
      var formatJournal = "";

      if (record.metadata.journal && record.metadata.journal.title) {
        formatJournal = "Published in " + record.metadata.journal.title;
        if (record.metadata.journal.volume) {
          formatJournal = formatJournal + ", vol. " + record.metadata.journal.volume;
        }
        if (record.metadata.journal.issue) {
          formatJournal = formatJournal + ", issue " + record.metadata.journal.issue;
        }
        if (record.metadata.journal.pages && record.metadata.journal.pages.includes("-")) {
          formatJournal = formatJournal + ", pp. " + record.metadata.journal.pages;
        }
        else if (record.metadata.journal.pages) {
          formatJournal = formatJournal + ", p. " + record.metadata.journal.pages;
        }
        formatJournal = formatJournal + ". "
      }

    return formatJournal;
    };
  }
  return formatJournalFilter;
});
