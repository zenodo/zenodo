# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2012, 2013 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""

PersistentIdentifier store and registration.

Usage example for registering new identifiers:

    from invenio.pidstore_model import PersistentIdentifier

    # Reserve a new DOI internally first
    pid = PersistentIdentifier.create('doi','10.0572/1234')

    # Get an already reserved DOI
    pid = PersistentIdentifier.get('doi', '10.0572/1234')

    # Assign it to a record.
    pid.assign('rec', 1234)

    url = "http://www.zenodo.org/record/1234"
    doc = "<resource ...."

    # Pre-reserve the DOI in DataCite
    pid.reserve(doc=doc)

    # Register the DOI (note parameters depended on the provider and pid type)
    pid.register(url=url, doc=doc)

    # Reassign DOI to new record
    pid.assign('rec', 5678, overwrite=True),

    # Update provider with new information
    pid.update(url, doc)

    # Delete the DOI (you shouldn't be doing this ;-)
    pid.delete()
"""


from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import url_for

from invenio.sqlalchemyutils import db
from invenio.textutils import decode_to_unicode
from invenio.pidstore_providers import PidProvider
#from invenio.pidstore_signals import before_save_collection, \


CFG_OBJECT_TYPES = ['rec', ]

CFG_STATUS_NEW = 'N'
""" The pid has *not* yet been registered with the service provider. """

CFG_STATUS_REGISTERED = 'R'
""" The pid has been registered with the service provider. """

CFG_STATUS_DELETED = 'D'
"""
The pid has been deleted with the service proivider. This should
very rarely happen, and must be kept track of, as the PID should not be
reused for something else.
"""

CFG_STATUS_RESERVED = 'K'
""" The pid has been reserved in the service provider but not yet fully
registered. """


#
# Utility method
#
def to_unicode(s):
    if isinstance(s, unicode):
        return s
    if isinstance(s, basestring):
        return decode_to_unicode(s)
    return unicode(s)


#
# Models
#
class PersistentIdentifier(db.Model):
    """
    Store and register persistent identifiers

    Assumptions:
      * Persistent identifiers can be represented as a string of max 255 chars.
      * An object has many persistent identifiers.
      * A persistent identifier has one and only one object.
    """

    __tablename__ = 'pid'
    __table_args__ = (
        db.Index('uidx_type_pid', 'type', 'pid', unique=True),
        db.Index('idx_status', 'status'),
        db.Index('', 'object_type', 'object_id'),
    )

    id = db.Column(db.Integer(15, unsigned=True), primary_key=True)
    """ Id of persistent identifier entry """

    type = db.Column(db.String(6), nullable=False)
    """ Persistent Identifier Scheme """

    pid = db.Column(db.String(length=255), nullable=False)
    """ Persistent Identifier """

    status = db.Column(db.Char(length=1), nullable=False)
    """ Status of persistent identifier, e.g. registered, reserved, deleted """

    object_type = db.Column(db.String(3), nullable=True)
    """ Object Type - e.g. rec for record """

    object_id = db.Column(db.String(length=255), nullable=True)
    """ Object ID - e.g. a record id """

    created = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    """ Creation datetime of entry """

    last_modified = db.Column(
        db.DateTime(), nullable=False, default=datetime.now,
        onupdate=datetime.now
    )
    """ Last modification datetime of entry """

    #
    # Class methods
    #
    @classmethod
    def create(cls, pid_type, pid, provider=None):
        """
        Internally reserve a new persistent identifier in Invenio.

        A provider for the given persistent identifier type must exists. By
        default the system will choose a provider according to the pid
        type. If desired, the default system provider can be overridden via
        the provider keyword argument.

        Returns PID object if successful otherwise None.
        """
        # Ensure provider exists
        if provider is None:
            provider = PidProvider.create(pid_type, pid)
            if not provider:
                raise Exception(
                    "No provider found for %s:%s" % (pid_type, pid)
                )

        try:
            obj = cls(type=provider.pid_type, pid=pid, status=CFG_STATUS_NEW)
            obj._provider = provider
            db.session.add(obj)
            db.session.commit()
            obj.log("CREATE", "Created")
            return obj
        except SQLAlchemyError:
            db.session.rollback()
            obj.log("CREATE", "Failed to created. Already exists.")
            return None

    @classmethod
    def get(cls, pid_type, pid, provider=None):
        """
        Get persistent identifier.

        Returns None if not found.
        """
        pid = to_unicode(pid)
        obj = cls.query.filter_by(type=pid_type, pid=pid).first()
        if obj:
            obj._provider = provider
            return obj
        else:
            return None

    #
    # Instance methods
    #
    def has_object(self, object_type, object_id):
        """
        Determine if this persistent identifier is assigned to a specific
        object.
        """
        if object_type not in CFG_OBJECT_TYPES:
            raise Exception("Invalid object type %s." % object_type)

        object_id = to_unicode(object_id)

        return self.object_type == object_type and self.object_id == object_id

    def get_provider(self):
        """
        Get the provider for this type of persistent identifier
        """
        if self._provider is None:
            self._provider = PidProvider.create(self.type, self.pid)
        return self._provider

    def assign(self, object_type, object_id, overwrite=False):
        """
        Assign this persistent identifier to a given object

        Note, the persistent identifier must first have been reserved. Also,
        if an exsiting object is already assigned to the pid, it will raise an
        exception unless overwrite=True.
        """
        if object_type not in CFG_OBJECT_TYPES:
            raise Exception("Invalid object type %s." % object_type)
        object_id = to_unicode(object_id)

        if not self.id:
            raise Exception("You must first create the persistent identifier before you can assign objects to it.")

        # FIXME: Desirable to not be able to assign to a deleted?
        if self.is_deleted():
            raise Exception("You cannot assign objects to a deleted persistent identifier.")

        # Check for an existing object assigned to this pid
        existing_obj_id = self.get_assigned_object(object_type)

        if existing_obj_id and existing_obj_id != object_id:
            if not overwrite:
                raise Exception("Persistent identifier is already assigned to another object")
            else:
                self.log("ASSIGN", "Unassigned object %s:%s (overwrite requested)" % (
                    self.object_type, self.object_id)
                )
                self.object_type = None
                self.object_id = None
        elif existing_obj_id and existing_obj_id == object_id:
            # The object is already assigned to this pid.
            return True

        self.object_type = object_type
        self.object_id = object_id
        db.session.commit()
        self.log("ASSIGN", "Assigned object %s:%s" % (self.object_type,
                                                      self.object_id))
        return True

    def update(self, with_deleted=False, *args, **kwargs):
        """ Update the persistent identifier with the provider. """
        if self.is_new() or self.is_reserved():
            raise Exception("Persistent identifier has not yet been registered.")

        if not with_deleted and self.is_deleted():
            raise Exception("Persistent identifier has been deleted.")

        provider = self.get_provider()
        if provider is None:
            self.log("UPDATE", "No provider found.")
            raise Exception("No provider found.")

        if provider.update(self, *args, **kwargs):
            if with_deleted and self.is_deleted():
                self.status = CFG_STATUS_REGISTERED
                db.session.commit()
            return True
        return False

    def reserve(self, *args, **kwargs):
        """
        Reserve the persistent identifier with the provider

        Note, the reserve method may be called multiple times, even if it was
        already reserved.
        """
        if not (self.is_new() or self.is_reserved()):
            raise Exception("Persistent identifier has already been registered.")

        provider = self.get_provider()
        if provider is None:
            self.log("RESERVE", "No provider found.")
            raise Exception("No provider found.")

        if provider.reserve(self, *args, **kwargs):
            self.status = CFG_STATUS_RESERVED
            db.session.commit()
            return True
        return False

    def register(self, *args, **kwargs):
        """
        Register the persistent identifier with the provider
        """
        if self.is_registered() or self.is_deleted():
            raise Exception("Persistent identifier has already been registered.")

        provider = self.get_provider()
        if provider is None:
            self.log("REGISTER", "No provider found.")
            raise Exception("No provider found.")

        if provider.register(self, *args, **kwargs):
            self.status = CFG_STATUS_REGISTERED
            db.session.commit()
            return True
        return False

    def delete(self, *args, **kwargs):
        """
        Delete the persistent identifier
        """
        if self.is_new():
            # New DOI which haven't been registered yet. Just delete it
            # completely but keep log)
            # Remove links to log entries (but otherwise leave the log entries)
            PidLog.query.filter_by(id_pid=self.id).update({'id_pid': None})
            db.session.delete(self)
            self.log("DELETE", "Unregistered PID successfully deleted")
        else:
            provider = self.get_provider()
            if not provider.delete(self, *args, **kwargs):
                return False
            self.status = CFG_STATUS_DELETED
            db.session.commit()
        return True

    def get_assigned_object(self, object_type=None):
        if object_type is not None and self.object_type == object_type:
            return self.object_id
        return None

    def is_registered(self):
        """ Returns true if the persistent identifier has been registered """
        return self.status == CFG_STATUS_REGISTERED

    def is_deleted(self):
        """ Returns true if the persistent identifier has been deleted """
        return self.status == CFG_STATUS_DELETED

    def is_new(self):
        """
        Returns true if the persistent identifier has not yet been
        registered or reserved
        """
        return self.status == CFG_STATUS_NEW

    def is_reserved(self):
        """
        Returns true if the persistent identifier has not yet been
        reserved.
        """
        return self.status == CFG_STATUS_RESERVED

    def log(self, action, message):
        if self.type and self.pid:
            message = "[%s:%s] %s" % (self.type, self.pid, message)
        p = PidLog(id_pid=self.id, action=action, message=message)
        db.session.add(p)
        db.session.commit()


class PidLog(db.Model):
    """
    Audit log of actions happening to persistent identifiers.

    This model is primarily used through PersistentIdentifier.log and rarely
    created manually.
    """
    __tablename__ = 'pidLOG'
    __table_args__ = (
        db.Index('idx_action', 'action'),
    )

    id = db.Column(db.Integer(15, unsigned=True), primary_key=True)
    """ Id of persistent identifier entry """

    id_pid = db.Column(
        db.Integer(15, unsigned=True), db.ForeignKey(PersistentIdentifier.id),
        nullable=True,
    )
    """ PID """

    timestamp = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    """ Creation datetime of entry """

    action = db.Column(db.String(10), nullable=False)
    """ Action identifier """

    message = db.Column(db.Text(), nullable=False)
    """ Log message """
