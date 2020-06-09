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

    def __init__(self, term_types=None, vocabularies=None):
        """Initialize custom metadata API object."""
        self._term_types = term_types or {}
        self._vocabularies = vocabularies or {}
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
    def available_vocabulary_set(self):
        """Get available vocabularies."""
        vocabulary = []
        for scheme in self.vocabularies:
            for value in self.vocabularies[scheme]['attributes']:
                vocabulary.append(u'{}:{}'.format(scheme, value))
        return set(vocabulary)

    @cached_property
    def terms(self):
        """Term-to-fieldtype lookup."""
        result = {}
        for vocab, cfg in self.vocabularies.items():
            vocab_url = cfg['@context']
            for attr in cfg['attributes']:
                term = u'{}:{}'.format(vocab, attr)
                term_conf = cfg['attributes'][attr]
                result[term] = dict(
                    term_conf,
                    url=u'{}{}'.format(vocab_url, attr)
                )
        return result

    def _validate(self):
        """Validates term types, vocabularies and definitions."""
        valid_term_types = set(self.term_types.keys())
        assert all(
            (v['@context'] and v['attributes'] and
             set([k['type'] for k in v['attributes'].values()]) <=
             valid_term_types)
            for k, v in self.vocabularies.items())
