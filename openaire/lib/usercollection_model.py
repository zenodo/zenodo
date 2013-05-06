# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012, 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
UserCollection Model - a layer around Invenio's collections
and portalboxes for easier allowing end-users to create their own collections.

    from invenio.usercollection_model import UserCollection
    from invenio.sqlalchemyutils import db

    u = UserCollection.query.get('test5')

    u = UserCollection(
        id='test5',
        id_user=176,
        title='European Middleware Initiative',
        description='Bla bla',
        curation_policy='Bla'
    )
    db.session.add(u)
    db.session.commit()
    u.save_collection(provisional=False)

After call to save_collection() you must do the following:
- Clear redis cache key for collection
- Run webcoll immediately for only this collection


"""

from datetime import datetime
from urllib import quote_plus

from invenio.config import CFG_SITE_LANG
from invenio.sqlalchemyutils import db
from invenio.websession_model import User
from invenio.websearch_model import \
    Collection, \
    Collectionname, \
    Collectiondetailedrecordpagetabs, \
    CollectionCollection, \
    Portalbox, \
    CollectionPortalbox, \
    Format, \
    CollectionFormat
from invenio.webaccess_model import \
    AccACTION, \
    AccROLE, \
    AccARGUMENT, \
    AccAuthorization, \
    UserAccROLE
from invenio.oai_harvest_model import OaiREPOSITORY
from invenio.jinja2utils import render_template_to_string
from invenio.usercollection_signals import before_save_collection, \
    after_save_collection, before_save_collections, after_save_collections, \
    before_delete_collection, after_delete_collection, \
    before_delete_collections, after_delete_collections
from invenio.search_engine import get_record, search_pattern, get_fieldvalues
from invenio.bibrecord import record_add_field
from flask import url_for
from invenio.bibuploadutils import bibupload_record

#
# Configuration variables
#
CFG_USERCOLLCTION_TABS = 'usage;comments;metadata;files'
""" Detailed record tabs to enable for a user collection """

CFG_USERCOLLCTION_PARENT_NAME = 'Communities'
""" Collection name of parent of public user collections """

CFG_USERCOLLCTION_PARENT_NAME_PROVISIONAL = 'Communities'
""" Collection name of parent of provisional user collections """

CFG_USERCOLLCTION_OUTPUTFORMAT = 'hb'
"""
Output format to use for collection, use empty string for default.
"""

CFG_USERCOLLCTION_OUTPUTFORMAT_PROVISIONAL = 'hbpro'
"""
Output format to use for provisional collection, use empty string for default.
"""

CFG_USERCOLLCTION_PORTALBOXES = [
    'usercollection_portalbox_main.html',
    'usercollection_portalbox_upload.html'
]
"""
List of templates to render as portalboxes for each collection - order of
portalboxes is given by order of templates.
"""

CFG_USERCOLLCTION_PORTALBOXES_PROVISIONAL = [
    'usercollection_portalbox_provisional.html',
]
"""
List of templates to render as portalboxes for each provisional collection -
order of portalboxes is given by order of templates.
"""

CFG_USERCOLLECTION_COLLECTION_TYPE = 'v'
""" Type of collections created (v, virtual or r, regular) """

CFG_USERCOLLECTION_COLLECTION_SCORE = 0
""" Default score used for ordering collections """

CFG_USERCOLLECTION_PORTALBOX_POSITION = 'rt'
""" Position of portal boxes """

CFG_USERCOLLECTION_ID_PREFIX = 'user'
""" Collection identifier prefix for all user collections """

CFG_USERCOLLECTION_ID_PREFIX_PROVISIONAL = 'provisional-user'
""" Collection identifier prefix for provisional user collections. """


class UserCollection(db.Model):
    """ Represents a user collection - a layer around
    Invenio's collections and portalboxes, that allow end-users to create
    """
    __tablename__ = 'userCOLLECTION'

    #
    # Fields
    #
    id = db.Column(db.String(100), primary_key=True)
    """ User collection identifier used to generate the real collection_identifier """

    id_user = db.Column(
        db.Integer(15, unsigned=True), db.ForeignKey(User.id),
        nullable=False
    )
    """ Owner of the collection. """

    id_collection = db.Column(
        db.Integer(15, unsigned=True), db.ForeignKey(Collection.id), nullable=True,
        default=None
    )
    """ Invenio collection generated from this collection """

    id_collection_provisional = db.Column(
        db.Integer(15, unsigned=True), db.ForeignKey(Collection.id), nullable=True,
        default=None
    )
    """ Invenio provisional collection generated from this collection """

    id_oairepository = db.Column(
        db.MediumInteger(9, unsigned=True), db.ForeignKey(OaiREPOSITORY.id),
        nullable=True, default=None
    )
    """ OAI Repository set specification """

    title = db.Column(db.String(length=255), nullable=False, default='')
    """ Title of collection. """

    description = db.Column(db.Text(), nullable=False, default='')
    """ Short description of collection, displayed in portal boxes. """

    page = db.Column(db.Text(), nullable=False, default='')
    """ Long description of collection, displayed on an individual page. """

    curation_policy = db.Column(db.Text(), nullable=False, default='')
    """ """

    has_logo = db.Column(db.Boolean(), nullable=False, default=False)
    """ """

    created = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    """ Creation datetime """

    last_modified = db.Column(db.DateTime(), nullable=False, default=datetime.now, onupdate=datetime.now)
    """ Last modification datetime """

    #
    # Relation ships
    #
    owner = db.relationship(User, backref='usercollections', foreign_keys=[id_user])
    """ Relation to the owner (User) of the collection """

    collection = db.relationship(
        Collection, uselist=False, backref='usercollection', foreign_keys=[id_collection]
    )
    """ Relationship to Invenio collection. """

    collection_provisional = db.relationship(
        Collection, uselist=False, backref='usercollection_provisional', foreign_keys=[id_collection_provisional]
    )
    """ Relationship to Invenio restricted collection containing uncurated records. """

    oai_set = db.relationship(
        OaiREPOSITORY, uselist=False, backref='usercollection', foreign_keys=[id_oairepository]
    )
    """ Relation to the owner (User) of the collection """

    #
    # Properties
    #
    @property
    def logo_url(self):
        """
        Get URL to collection logo
        """
        # FIXME
        if self.has_logo:
            raise NotImplementedError
        else:
            return None

    @property
    def oai_url(self):
        """ Get link to OAI-PMH API for this user collection """
        return "/oai2d?verb=ListRecords&metadataPrefix=oai_dc&set=%s" % self.get_collection_name()

    @property
    def collection_url(self):
        """ Get URL to collection """
        return "/collection/%s" % self.get_collection_name()

    @property
    def collection_provisional_url(self):
        """ Get URL to provisional collection """
        return "/search?cc=%s" % self.get_collection_name(provisional=True)

    @property
    def upload_url(self):
        """ Get direct upload URL """
        return url_for('deposit.index', c=self.id)

    #
    # Utility methods
    #
    def get_collection_name(self, provisional=False):
        """ Get a unique collection name identifier """
        if provisional:
            return "%s-%s" % (CFG_USERCOLLECTION_ID_PREFIX_PROVISIONAL, self.id)
        else:
            return "%s-%s" % (CFG_USERCOLLECTION_ID_PREFIX, self.id)

    def get_title(self, provisional=False):
        if provisional:
            return "Provisional: %s" % self.title
        else:
            return self.title

    def get_collection_dbquery(self, provisional=False):
        """ Get collection query """
        return "%s:%s" % self.get_query(provisional=provisional)

    def get_query(self, provisional=False):
        """ Get tuple (field,value) for search engine query """
        return ("980__a", self.get_collection_name(provisional=provisional))

    def render_portalbox_bodies(self, templates):
        """
        Get a list of rendered portal boxes for this user collection
        """
        ctx = {
            'usercollection': self,
        }

        return map(
            lambda t: render_template_to_string(t, **ctx),
            templates
        )

    #
    # Curation methods
    #
    def _modify_record(self, recid, test_func, replace_func, include_func):
        """
        Generate record a MARCXML file and upload it

        @param test_func: Function to test if a collection id should be changed
        @param replace_func: Function to replace the collection id.
        @param include_func: Function to test if collection should be included
        """
        rec = get_record(recid)
        newcolls = []
        dirty = False

        try:
            colls = rec['980']
            for c in colls:
                try:
                    # We are only interested in subfield 'a'
                    code, val = c[0][0]
                    if test_func(code, val):
                        c[0][0] = replace_func(code, val)
                        dirty = True
                    if include_func(code, val):
                        newcolls.append(c[0])
                    else:
                        dirty = True
                except IndexError:
                    pass
        except KeyError:
            return False

        if not dirty:
            return False

        rec = {}
        record_add_field(rec, '001', controlfield_value=str(recid))

        for subfields in newcolls:
            record_add_field(rec, '980', subfields=subfields)

        return rec

    def _upload_record(self, rec):
        """
        Bibupload one record
        """
        bibupload_record(
            record=rec, file_prefix='usercoll', mode='-c',
            opts=['-n', '-P5']
        )
        return True

    def _upload_collection(self, coll):
        """
        Bibupload many records
        """
        bibupload_record(
            collection=coll, file_prefix='usercoll', mode='-c',
            opts=['-n', '-P5']
        )
        return True

    def accept_record(self, recid):
        """
        Accept a record for inclusion in a user collection

        @param recid: Record ID
        """
        expected_id = self.get_collection_name(provisional=True)
        new_id = self.get_collection_name(provisional=False)

        def test_func(code, val):
            return code == 'a' and val == expected_id

        def replace_func(code, val):
            return (code, new_id)

        def include_func(code, val):
            return True

        return self._upload_record(self._modify_record(recid, test_func, replace_func, include_func))

    def reject_record(self, recid):
        """
        Reject a record for inclusion in a user collection

        @param recid: Record ID
        """
        expected_id = self.get_collection_name(provisional=True)
        new_id = self.get_collection_name(provisional=False)

        def test_func(code, val):
            return False

        def replace_func(code, val):
            return (code, val)

        def include_func(code, val):
            return not (code == 'a' and (val == expected_id or val == new_id))

        return self._upload_record(self._modify_record(recid, test_func, replace_func, include_func))

    #
    # Data persistence methods
    #
    def save_collectionname(self, collection, title):
        """
        Create or update Collectionname object
        """
        if collection.id:
            c_name = Collectionname.query.filter_by(
                id_collection=collection.id, ln=CFG_SITE_LANG, type='ln'
            ).first()
            if c_name:
                update_changed_fields(c_name, dict(value=title))
                return c_name

        c_name = Collectionname(
            collection=collection,
            ln=CFG_SITE_LANG,
            type='ln',
            value=title,
        )
        db.session.add(c_name)
        return c_name

    def save_collectiondetailedrecordpagetabs(self, collection):
        """
        Create or update Collectiondetailedrecordpagetabs object
        """
        if collection.id:
            c_tabs = Collectiondetailedrecordpagetabs.query.filter_by(
                id_collection=collection.id
            ).first()
            if c_tabs:
                update_changed_fields(c_tabs, dict(tabs=CFG_USERCOLLCTION_TABS))
                return c_tabs

        c_tabs = Collectiondetailedrecordpagetabs(
            collection=collection,
            tabs=CFG_USERCOLLCTION_TABS,
        )
        db.session.add(c_tabs)
        return c_tabs

    def save_collectioncollection(self, collection, parent_name):
        """
        Create or update CollectionCollection object
        """
        dad = Collection.query.filter_by(name=parent_name).first()

        if collection.id:
            c_tree = CollectionCollection.query.filter_by(
                id_dad=dad.id,
                id_son=collection.id
            ).first()
            if c_tree:
                update_changed_fields(c_tree, dict(type=CFG_USERCOLLECTION_COLLECTION_TYPE, score=CFG_USERCOLLECTION_COLLECTION_SCORE))
                return c_tree

        c_tree = CollectionCollection(
            dad=dad,
            son=collection,
            type=CFG_USERCOLLECTION_COLLECTION_TYPE,
            score=CFG_USERCOLLECTION_COLLECTION_SCORE,
        )
        db.session.add(c_tree)
        return c_tree

    def save_collectionformat(self, collection, fmt_str):
        """
        Create or update CollectionFormat object
        """
        fmt = Format.query.filter_by(code=fmt_str).first()

        if collection.id:
            c_fmt = CollectionFormat.query.filter_by(
                id_collection=collection.id
            ).first()
            if c_fmt:
                update_changed_fields(c_fmt, dict(id_format=fmt.id, score=1))
                return c_fmt

        c_fmt = CollectionFormat(
            collection=collection,
            format=fmt,
        )
        db.session.add(c_fmt)
        return c_fmt

    def save_collectionportalboxes(self, collection, templates):
        """
        Create or update Portalbox and CollectionPortalbox objects
        """
        # Setup portal boxes
        bodies = self.render_portalbox_bodies(templates)
        bodies.reverse()  # Highest score is on the top, so we reverse the list

        objects = []
        if collection.id:
            c_pboxes = CollectionPortalbox.query.filter_by(
                id_collection=collection.id,
                ln=CFG_SITE_LANG,
            ).all()
            if len(c_pboxes) == len(bodies):
                for score, elem in enumerate(zip(c_pboxes, bodies)):
                    c_pbox, body = elem
                    pbox = c_pbox.portalbox
                    update_changed_fields(pbox, dict(body=body))
                    update_changed_fields(c_pbox, dict(score=score, position=CFG_USERCOLLECTION_PORTALBOX_POSITION))
                    objects.append(c_pbox)
                return objects
            else:
                # Either templates where modified or collection portalboxes
                # where modified outside of the UserCollection. In either case,
                # remove existing portalboxes and add new ones.
                for c_pbox in c_pboxes:
                    db.session.delete(c_pbox.portalbox)
                    db.session.delete(c_pbox)

        for score, body in enumerate(bodies):
            p = Portalbox(title='', body=body)
            c_pbox = CollectionPortalbox(None, None, None, None, None)
            update_changed_fields(c_pbox, dict(
                collection=collection,
                portalbox=p,
                ln=CFG_SITE_LANG,
                position=CFG_USERCOLLECTION_PORTALBOX_POSITION,
                score=score,
            ))
            db.session.add_all([p, c_pbox])
            objects.append(c_pbox)
        return objects

    def save_oairepository_set(self, provisional=False):
        """
        Create or update OAI Repository set.
        """
        collection_name = self.get_collection_name(provisional=provisional)
        (f1, p1) = self.get_query(provisional=provisional)
        fields = dict(
            setName='%s set' % collection_name,
            setSpec=collection_name,
            setDescription=self.description,
            p1=p1, f1=f1, m1='e',
            p2='', f2='', m2='',
            p3='', f3='', m3='',
        )

        if self.oai_set:
            update_changed_fields(self.oai_set, fields)
        else:
            self.oai_set = OaiREPOSITORY(**fields)
            db.session.add(self.oai_set)

    def save_acl(self, collection_id, collection_name):
        """
        Create or update authorization for user to view the provisional collection
        """
        # Role - use collection id, because role name is limited to 32 chars.
        role_name = 'coll_%s' % collection_id
        role = AccROLE.query.filter_by(name=role_name).first()
        if not role:
            role = AccROLE(name=role_name, description='Curators of collection %s' % collection_name)
            db.session.add(role)

        # Argument
        fields = dict(keyword='collection', value=collection_name)
        arg = AccARGUMENT.query.filter_by(**fields).first()
        if not arg:
            arg = AccARGUMENT(**fields)
            db.session.add(arg)

        # Action
        action = AccACTION.query.filter_by(name='viewrestrcoll').first()

        # User role
        alluserroles = UserAccROLE.query.filter_by(role=role).all()
        userrole = None
        if alluserroles:
            # Remove any user which is not the owner
            for ur in alluserroles:
                if ur.id_user == self.id_user:
                    db.session.delete(ur)
                else:
                    userrole = ur

        if not userrole:
            userrole = UserAccROLE(user=self.owner, role=role)
            db.session.add(userrole)

        # Authorization
        auth = AccAuthorization.query.filter_by(role=role, action=action, argument=arg).first()
        if not auth:
            auth = AccAuthorization(role=role, action=action, argument=arg, argumentlistid=1)

    def save_collection(self, provisional=False):
        """
        Create or update a new collection with name, tabs, collection tree,
        collection output formats, portalboxes and OAI repository set
        """
        # Setup collection
        collection_name = self.get_collection_name(provisional=provisional)
        c = Collection.query.filter_by(name=collection_name).first()
        fields = dict(
            name=collection_name,
            dbquery=self.get_collection_dbquery(provisional=provisional)
        )

        if c:
            before_save_collection.send(self, is_new=True, provisional=provisional)
            update_changed_fields(c, fields)
        else:
            before_save_collection.send(self, is_new=False, provisional=provisional)
            c = Collection(**fields)
            db.session.add(c)
            db.session.commit()
        setattr(self, 'collection_provisional' if provisional else 'collection', c)

        # Setup OAI Repository
        if provisional:
            self.save_acl(c.id, collection_name)
        else:
            self.save_oairepository_set(provisional=provisional)

        # Setup title, tabs and collection tree
        self.save_collectionname(c, self.get_title(provisional=provisional))
        self.save_collectiondetailedrecordpagetabs(c)
        self.save_collectioncollection(
            c,
            CFG_USERCOLLCTION_PARENT_NAME_PROVISIONAL if provisional else CFG_USERCOLLCTION_PARENT_NAME
        )

        # Setup collection format is needed
        if not provisional and CFG_USERCOLLCTION_OUTPUTFORMAT:
            self.save_collectionformat(c, CFG_USERCOLLCTION_OUTPUTFORMAT)
        elif provisional and CFG_USERCOLLCTION_OUTPUTFORMAT_PROVISIONAL:
            self.save_collectionformat(c, CFG_USERCOLLCTION_OUTPUTFORMAT_PROVISIONAL)

        # Setup portal boxes
        self.save_collectionportalboxes(
            c,
            CFG_USERCOLLCTION_PORTALBOXES_PROVISIONAL if provisional else CFG_USERCOLLCTION_PORTALBOXES
        )
        db.session.commit()
        after_save_collection.send(self, collection=c, provisional=provisional)

    def save_collections(self):
        """
        Create restricted and unrestricted collection
        """
        before_save_collections.send(self)
        self.save_collection(provisional=False)
        self.save_collection(provisional=True)
        after_save_collections.send(self)

    def delete_record_collection_identifiers(self):
        """
        Remove collection identifiers for this user collection from all records.
        """
        provisional_id = self.get_collection_name(provisional=True)
        normal_id = self.get_collection_name(provisional=False)

        def test_func(code, val):
            return False

        def replace_func(code, val):
            return (code, val)

        def include_func(code, val):
            return not (code == 'a' and (val == provisional_id or val == normal_id))

        coll = []
        for r in search_pattern(p="980__a:%s OR 980__a:%s" % (normal_id, provisional_id)):
            coll.append(
                self._modify_record(r, test_func, replace_func, include_func)
            )

        self._upload_collection(coll)

    def delete_collection(self, provisional=False):
        """
        Delete all objects related to a single collection
        """
        # Most of the logic in this method ought to be moved to a
        # Collection.delete() method.
        c = getattr(self, "collection_provisional" if provisional else "collection")
        collction_name = self.get_collection_name(provisional=provisional)

        before_delete_collection.send(self, collection=c, provisional=provisional)

        if c:
            # Delete portal boxes
            for c_pbox in c.portalboxes:
                if c_pbox.portalbox:
                    db.session.delete(c_pbox.portalbox)
                db.session.delete(c_pbox)

            # Delete output formats:
            CollectionFormat.query.filter_by(id_collection=c.id).delete()

            # Delete title, tabs, collection tree
            Collectionname.query.filter_by(id_collection=c.id).delete()
            CollectionCollection.query.filter_by(id_son=c.id).delete()
            Collectiondetailedrecordpagetabs.query.filter_by(id_collection=c.id).delete()

        if provisional:
            # Delete ACLs
            AccARGUMENT.query.filter_by(keyword='collection', value=collction_name).delete()
            role = AccROLE.query.filter_by(name='coll_%s' % c.id).first()
            if role:
                UserAccROLE.query.filter_by(role=role).delete()
                AccAuthorization.query.filter_by(role=role).delete()
                db.session.delete(role)
        else:
            # Delete OAI repository
            if self.oai_set:
                db.session.delete(self.oai_set)

        # Delete collection
        if c:
            db.session.delete(c)
        db.session.commit()
        after_delete_collection.send(self, provisional=provisional)

    def delete_collections(self):
        """
        Delete collection and all associated objects.
        """
        before_delete_collections.send(self)
        self.delete_record_collection_identifiers()
        self.delete_collection(provisional=False)
        self.delete_collection(provisional=True)
        after_delete_collections.send(self)


def update_changed_fields(obj, fields):
    """
    Utility method to update fields on an object if they have changed, and
    report back if any changes where made.
    """
    dirty = False
    for attr, newval in fields.items():
        val = getattr(obj, attr)
        if val != newval:
            setattr(obj, attr, newval)
            dirty = True
    return dirty
