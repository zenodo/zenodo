# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""
User collection signals - useful for hooking into the collection
creation process.
"""

from blinker import Namespace
_signals = Namespace()

before_save_collection = _signals.signal('before-save-collection')
"""
This signal is sent right before collection is saved.
Sender is the user collection. Extra data pass is:

 * is_new
 * provisional
"""

after_save_collection = _signals.signal('after-save-collection')
"""
This signal is sent right after a collection is saved.
Sender is the user collection. Extra data pass is:

 * collection
 * provisional
"""

before_save_collections = _signals.signal('before-save-collections')
"""
This signal is sent right before all collections are saved.
Sender is the user collection.
"""

after_save_collections = _signals.signal('after-save-collections')
"""
This signal is sent right after all collections are saved.
Sender is the user collection.
"""

before_delete_collection = _signals.signal('before-delete-collection')
"""
This signal is sent right before a collection is deleted.
Sender is the user collection. Extra data pass is:

 * collection
 * provisional
"""

after_delete_collection = _signals.signal('after-delete-collection')
"""
This signal is sent right after a collection is deleted.
Sender is the user collection. Extra data pass is:

 * provisional
"""

before_delete_collections = _signals.signal('before-delete-collection')
"""
This signal is sent right before all collections are deleted.
Sender is the user collection.
"""

after_delete_collections = _signals.signal('after-delete-collection')
"""
This signal is sent right after all collections are deleted.
Sender is the user collection.
"""


pre_curation = _signals.signal('pre-curation')
"""
This signal is sent right before a record is accepted or rejected.
Sender is the user collection. Extra data pass is:

 * action: accept or reject
 * recid: Record ID
 * pretend: True if record changes is actually not persisted
"""

post_curation = _signals.signal('post-curation')
"""
This signal is sent right after a record is accepted or rejected.
Sender is the user collection.

 * action: accept or reject
 * recid:  Record ID
 * record: Record which was uploaded
 * pretend: True if record changes is actually not persisted

Note, the record which was accept/reject is most likely not updated
yet in the database, since bibupload has to run first.
"""
