# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Test Zenodo SIPStore."""

from __future__ import absolute_import, print_function

import json

from helpers import publish_and_expunge
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier
from invenio_sipstore.api import SIP
from invenio_sipstore.archivers import BagItArchiver
from invenio_sipstore.models import SIP as SIPModel
from six import BytesIO, b

from zenodo.modules.deposit.api import ZenodoDeposit
from zenodo.modules.sipstore.tasks import archive_sip
from zenodo.modules.sipstore.utils import generate_bag_path


def fetch_suff(sip, filename_suffix):
    """A helper method for fetching SIPFiles by the name suffix."""
    return next(f for f in sip.files if f.filepath.endswith(filename_suffix))


def get_m_item(meta, path):
    """Get metadata item by path name."""
    return next(it for it in meta if it['filepath'] == path)


def test_archiving(app, db, deposit, deposit_file, locations, archive_fs):
    """Test ZenodoSIP archiving."""
    deposit.files['test2.txt'] = BytesIO(b'test-two')
    deposit_v1 = publish_and_expunge(db, deposit)
    recid_v1, record_v1 = deposit_v1.fetch_published()
    recid_v1_id = recid_v1.id
    # Record files after publishing: 'test.txt', 'test2.txt'

    sip1 = SIP(SIPModel.query.one())
    sip1_id = sip1.id

    # Edit the metadata
    deposit_v1 = deposit_v1.edit()
    deposit_v1['title'] = "New title"
    deposit_v1 = publish_and_expunge(db, deposit_v1)
    # Record files after publishing: 'test.txt', 'test2.txt'
    sip2_id = SIPModel.query.order_by(SIPModel.created.desc()).first().id

    # Create a new version
    deposit_v1.newversion()
    recid_v1 = PersistentIdentifier.query.get(recid_v1_id)
    pv = PIDVersioning(child=recid_v1)
    depid_v2 = pv.draft_child_deposit
    deposit_v2 = ZenodoDeposit.get_record(depid_v2.object_uuid)
    del deposit_v2.files['test.txt']
    deposit_v2.files['test3.txt'] = BytesIO(b('test-three'))
    deposit_v2 = publish_and_expunge(db, deposit_v2)
    # Record files after publishing: 'test2.txt', 'test3.txt'

    sip1 = SIP(SIPModel.query.get(sip1_id))
    sip2 = SIP(SIPModel.query.get(sip2_id))
    sip3 = SIP(SIPModel.query.order_by(SIPModel.created.desc()).first())

    # Becase we are using secure_filename when writing SIPFiles we need to
    # genenarate the correct names: <SIPFile.id>-<secure_filename>
    s1_file1_fn = '{0}-test.txt'.format(fetch_suff(sip1, 'test.txt').file_id)
    s1_file1_fp = 'data/files/{0}'.format(s1_file1_fn)

    s1_file2_fn = '{0}-test2.txt'.format(fetch_suff(sip1, 'test2.txt').file_id)
    s1_file2_fp = 'data/files/{0}'.format(s1_file2_fn)

    s3_file2_fn = '{0}-test2.txt'.format(fetch_suff(sip3, 'test2.txt').file_id)
    s3_file2_fp = 'data/files/{0}'.format(s3_file2_fn)

    s3_file3_fn = '{0}-test3.txt'.format(fetch_suff(sip3, 'test3.txt').file_id)
    s3_file3_fp = 'data/files/{0}'.format(s3_file3_fn)

    sip1_bagmeta = json.loads(next(
        m.content for m in sip1.metadata if m.type.name == 'bagit'))['files']
    sip2_bagmeta = json.loads(next(
        m.content for m in sip2.metadata if m.type.name == 'bagit'))['files']
    sip3_bagmeta = json.loads(next(
        m.content for m in sip3.metadata if m.type.name == 'bagit'))['files']

    # Check if Bagit metadata contains the correct file-fetching information
    assert set([f['filepath'] for f in sip1_bagmeta]) == \
        set([s1_file1_fp,
             s1_file2_fp,
             'data/filenames.txt',
             'data/metadata/record-json.json', 'bag-info.txt',
             'manifest-md5.txt', 'bagit.txt', 'tagmanifest-md5.txt'])
    assert not BagItArchiver._is_fetched(
        get_m_item(sip1_bagmeta, s1_file1_fp))
    assert not BagItArchiver._is_fetched(
        get_m_item(sip1_bagmeta, s1_file2_fp))

    assert set([f['filepath'] for f in sip2_bagmeta]) == \
        set([s1_file1_fp,
             s1_file2_fp,
             'data/filenames.txt',
             'data/metadata/record-json.json', 'bag-info.txt',
             'manifest-md5.txt', 'bagit.txt', 'tagmanifest-md5.txt',
             'fetch.txt'])
    # Both files should be fetched since it's only metadata-edit submission
    assert BagItArchiver._is_fetched(
        get_m_item(sip2_bagmeta, s1_file1_fp))
    assert BagItArchiver._is_fetched(
        get_m_item(sip2_bagmeta, s1_file2_fp))

    assert set([f['filepath'] for f in sip3_bagmeta]) == \
        set([s3_file2_fp,
             s3_file3_fp,
             'data/filenames.txt',
             'data/metadata/record-json.json', 'bag-info.txt',
             'manifest-md5.txt', 'bagit.txt', 'tagmanifest-md5.txt',
             'fetch.txt'])

    # First file should be fetched from previous version and new file should
    # be archived in this bag.
    assert BagItArchiver._is_fetched(
        get_m_item(sip3_bagmeta, s3_file2_fp))
    assert not BagItArchiver._is_fetched(
        get_m_item(sip3_bagmeta, s3_file3_fp))
    archiver1 = BagItArchiver(sip1)
    archiver2 = BagItArchiver(sip2)
    archiver3 = BagItArchiver(sip3)

    # Each archiver subpath follows: '<recid>/r/<revision_id>'
    assert archiver1._get_archive_subpath() == '2/r/0'
    assert archiver2._get_archive_subpath() == '2/r/1'
    assert archiver3._get_archive_subpath() == '3/r/0'

    # As a test, write the SIPs in reverse chronological order
    assert not sip1.archived
    assert not sip2.archived
    assert not sip3.archived
    archive_sip.delay(sip3.id)
    archive_sip.delay(sip2.id)
    archive_sip.delay(sip1.id)
    assert sip1.archived
    assert sip2.archived
    assert sip3.archived

    fs1 = archive_fs.opendir(archiver1._get_archive_subpath())
    assert set(fs1.listdir()) == set(['tagmanifest-md5.txt', 'bagit.txt',
                                      'manifest-md5.txt', 'bag-info.txt',
                                      'data'])
    assert set(fs1.listdir('data')) == set(['metadata', 'files',
                                            'filenames.txt'])
    assert fs1.listdir('data/metadata') == ['record-json.json', ]
    assert set(fs1.listdir('data/files')) == set([s1_file1_fn, s1_file2_fn])

    fs2 = archive_fs.opendir(archiver2._get_archive_subpath())
    assert set(fs2.listdir()) == set(['tagmanifest-md5.txt', 'bagit.txt',
                                      'manifest-md5.txt', 'bag-info.txt',
                                      'data', 'fetch.txt'])
    # Second SIP has written only the metadata,
    # because of that There should be no 'files/', but 'filesnames.txt' should
    # still be there becasue of the fetch.txt
    assert set(fs2.listdir('data')) == set(['metadata', 'filenames.txt'])
    assert fs2.listdir('data/metadata') == ['record-json.json', ]

    with fs2.open('fetch.txt') as fp:
        cnt = fp.read().splitlines()
    # Fetched files should correctly fetch the files from the first archive
    base_uri = archiver1._get_archive_base_uri()
    assert set(cnt) == set([
        '{base}/2/r/0/{fn} 4 {fn}'.format(fn=s1_file1_fp, base=base_uri),
        '{base}/2/r/0/{fn} 8 {fn}'.format(fn=s1_file2_fp, base=base_uri),
    ])

    fs3 = archive_fs.opendir(archiver3._get_archive_subpath())
    assert set(fs3.listdir()) == set(['tagmanifest-md5.txt', 'bagit.txt',
                                      'manifest-md5.txt', 'bag-info.txt',
                                      'data', 'fetch.txt'])
    # Third SIP should write only the extra 'test3.txt' file
    assert set(fs3.listdir('data')) == set(['metadata', 'files',
                                            'filenames.txt'])
    assert fs3.listdir('data/metadata') == ['record-json.json', ]
    assert fs3.listdir('data/files') == [s3_file3_fn, ]
    with fs3.open('fetch.txt') as fp:
        cnt = fp.read().splitlines()
    # Since 'file.txt' was removed in third SIP, we should only fetch the
    # 'test2.txt', also from the first archive, since that's where this
    # file resides physically.
    base_uri = archiver1._get_archive_base_uri()
    assert set(cnt) == set([
        '{base}/2/r/0/{fn} 8 {fn}'.format(fn=s3_file2_fp, base=base_uri),
    ])


def test_bag_path_generator():
    """Test the bag path generator function."""
    assert generate_bag_path('1', '1') == ['1', 'r', '1', ]
    assert generate_bag_path('100', '1') == ['100', 'r', '1', ]
    assert generate_bag_path('1000', '1') == ['100', '0', 'r', '1', ]
    assert generate_bag_path('1234567890', '9999') == \
        ['123', '456', '789', '0', 'r', '9999', ]
