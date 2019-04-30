# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2019 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Custom metadata utilities."""

from werkzeug.utils import cached_property

from zenodo.modules.utils import obj_or_import_string


class CustomMetadataAPI(object):
    """Custom metadata helper class."""

    def __init__(self, term_types=None, vocabularies=None, definitions=None):
        """Initialize custom metadata API object."""
        self._term_types = term_types or {}
        self._vocabularies = vocabularies or {}
        self._definitions = definitions or {}
        self._validate()

    @cached_property
    def term_types(self):
        """Get available field types."""
        return {k: obj_or_import_string(v)
                for k, v in self._term_types.items()}

    @cached_property
    def vocabularies(self):
        """Get available vocabularies."""
        return self._vocabularies

    @cached_property
    def terms(self):
        """Term-to-fieldtype lookup."""
        result = {}
        for vocab, cfg in self.vocabularies.items():
            for attr, term_type in cfg['attributes'].items():
                term = '{}:{}'.format(vocab, attr)
                result[term] = term_type
        return result

    @cached_property
    def definitions(self):
        """Get available definitions."""
        return {k: set(v) for k, v in self._definitions.items()}

    def _validate(self):
        """Validates term types, vocabularies and definitions."""
        valid_term_types = set(self.term_types.keys())
        valid_terms = set(self.terms.keys())
        assert all(
            (v['@context'] and v['attributes'] and
             set(v['attributes'].values()) <= valid_term_types)
            for k, v in self.vocabularies.items())
        assert all(
            set(comm_terms) <= valid_terms
            for comm, comm_terms in self.definitions.items())
