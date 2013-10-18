# -*- coding: utf-8 -*-
#
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


from invenio.sqlalchemyutils import db
from invenio.testutils import make_test_suite, run_test_suite, \
    InvenioTestCase


class UserCollectionTest(InvenioTestCase):

    def validate_objects(self, u):
        from invenio.usercollection_model import UserCollection, \
            CFG_USERCOLLCTION_OUTPUTFORMAT, \
            CFG_USERCOLLCTION_OUTPUTFORMAT_PROVISIONAL, \
            CFG_USERCOLLCTION_PARENT_NAME, \
            CFG_USERCOLLCTION_PARENT_NAME_PROVISIONAL, \
            CFG_USERCOLLCTION_TABS
        from invenio.websearch_model import Collection, Collectionname, \
            Collectiondetailedrecordpagetabs, \
            CollectionCollection, CollectionPortalbox, \
            CollectionFormat
        from invenio.oai_harvest_model import OaiREPOSITORY
        from invenio.webaccess_model import \
            AccACTION, \
            AccROLE, \
            AccARGUMENT, \
            AccAuthorization, \
            UserAccROLE

        usercoll_id = u.id
        u = UserCollection.query.filter_by(id=usercoll_id).first()
        assert u.id == usercoll_id

        # Test collections
        c1 = Collection.query.filter_by(
            name=u.get_collection_name(provisional=False)
        ).first()
        assert c1.name == u.get_collection_name(provisional=False)
        assert c1.dbquery == '980__a:%s' % c1.name

        c2 = Collection.query.filter_by(
            name=u.get_collection_name(provisional=True)
        ).first()
        assert c2.name == u.get_collection_name(provisional=True)

        # Test OAI Repository
        oai = OaiREPOSITORY.query.filter_by(
            setSpec=u.get_collection_name(provisional=False)
        ).first()
        assert oai.p1
        assert oai.f1

        # Test format
        cfmt = CollectionFormat.query.filter_by(
            id_collection=c1.id
        ).first()
        assert cfmt.format.code == CFG_USERCOLLCTION_OUTPUTFORMAT

        cfmt = CollectionFormat.query.filter_by(
            id_collection=c2.id
        ).first()
        assert cfmt.format.code == CFG_USERCOLLCTION_OUTPUTFORMAT_PROVISIONAL

        # Portalbox
        cpboxes = CollectionPortalbox.query.filter_by(
            id_collection=c1.id
        ).all()
        for cpbox in cpboxes:
            assert cpbox.portalbox.body

        # Tabs
        c_tabs = Collectiondetailedrecordpagetabs.query.filter_by(
            id_collection=c1.id
        ).first()
        assert c_tabs.tabs == CFG_USERCOLLCTION_TABS

        c_tabs = Collectiondetailedrecordpagetabs.query.filter_by(
            id_collection=c2.id
        ).first()
        assert c_tabs.tabs == CFG_USERCOLLCTION_TABS

        # Name
        c_name = Collectionname.query.filter_by(id_collection=c1.id).first()
        assert c_name.value == u.title

        c_name = Collectionname.query.filter_by(id_collection=c2.id).first()
        assert c_name.value == u.get_title(provisional=True)

        # Hierarchy
        cc = CollectionCollection.query.filter_by(id_son=c1.id).first()
        assert cc.dad.name == CFG_USERCOLLCTION_PARENT_NAME

        cc = CollectionCollection.query.filter_by(id_son=c2.id).first()
        assert cc.dad.name == CFG_USERCOLLCTION_PARENT_NAME_PROVISIONAL

        # ACL
        role_name = u.get_role_name(c2.id)
        role = AccROLE.query.filter_by(name=role_name).first()
        assert role.name == role_name

        role_name = u.get_role_name(c2.id)
        role = AccROLE.query.filter_by(name=role_name).first()
        assert role.name == role_name

        arg = AccARGUMENT.query.filter_by(
            keyword='collection',
            value=c2.name
        ).first()
        assert arg.value == c2.name

        action = AccACTION.query.filter_by(name='viewrestrcoll').first()
        auth = AccAuthorization.query.filter_by(
            role=role, action=action, argument=arg
        ).first()
        assert auth.role

        # User roles
        roles = UserAccROLE.query.filter_by(role=role).all()
        assert len(roles) == 1
        assert roles[0].id_user == u.id_user

    def validate_no_objects(self, u):
        from invenio.websearch_model import Collection
        from invenio.oai_harvest_model import OaiREPOSITORY

        # Test collections
        c1 = Collection.query.filter_by(
            name=u.get_collection_name(provisional=False)
        ).first()
        assert not c1

        c2 = Collection.query.filter_by(
            name=u.get_collection_name(provisional=True)
        ).first()
        assert not c2

        # Test OAI Repository
        oai = OaiREPOSITORY.query.filter_by(
            setSpec=u.get_collection_name(provisional=False)
        ).first()
        assert not oai

    def test_create_delete(self):
        from invenio.usercollection_model import UserCollection

        usercoll_id = 'test-community'

        u = UserCollection(
            id=usercoll_id,
            title="Test Title",
            description="Test Description",
            curation_policy="Test Policy",
            page="Test Page",
            id_user=176
        )
        db.session.add(u)
        db.session.commit()
        u.save_collections()
        self.validate_objects(u)

        assert u.oai_url
        assert u.collection_url
        assert u.collection_provisional_url
        assert u.upload_url

        u.delete_collections()
        self.validate_no_objects(u)
        db.session.delete(u)
        db.session.commit()


TEST_SUITE = make_test_suite(UserCollectionTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
