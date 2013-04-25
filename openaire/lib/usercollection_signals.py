# -*- coding: utf-8 -*-

## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

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
