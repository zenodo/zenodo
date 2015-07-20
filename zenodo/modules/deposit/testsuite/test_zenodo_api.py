# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2014, 2015 CERN.
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

from cerberus import Validator
from invenio.testsuite import make_test_suite, run_test_suite, \
    make_pdf_fixture
from datetime import date, timedelta
from flask import url_for

from invenio.ext.restful.utils import APITestCase
from invenio.ext.sqlalchemy import db


class DepositApiTestCase(APITestCase):
    def setUp(self):
        """ Create API key """
        from invenio.modules.accounts.models import User
        self.user = User(
            email='info@invenio-software.org', nickname='tester'
        )
        self.user.password = "tester"
        db.session.add(self.user)
        db.session.commit()

        self.create_oauth_token(self.user.id, scopes=[
            "deposit:write", "deposit:actions"
        ])

    def tearDown(self):
        self.remove_oauth_token()
        if self.user:
            db.session.delete(self.user)
            db.session.commit()


class WebDepositApiTest(DepositApiTestCase):
    def test_depositions_list_get(self):
        response = self.get('depositionlistresource', code=200)
        # Test cookies are not being set
        self.assertFalse('Set-Cookie' in response.headers)

    def test_depositions_list_post_invalid(self):
        from invenio.modules.deposit.models import Deposition

        # Invalid arguments
        cases = [
            (1, {'unknownkey': 'data', 'metadata': {}}),
            (1, {'metadat': {}}),
        ]
        for num_errors, test_data in cases:
            response = self.post(
                'depositionlistresource', data=test_data, code=400
            )
            self.assertTrue(response.json['message'])
            self.assertTrue(response.json['errors'])
            self.assertEqual(response.json['status'], 400)
            self.assertEqual(len(response.json['errors']), num_errors)

        num_deps_before = len(Deposition.get_depositions())
        # Invalid form data
        response = self.post(
            'depositionlistresource', data={'metadata': {}}, code=400
        )
        num_deps_after = len(Deposition.get_depositions())
        self.assertEqual(num_deps_before, num_deps_after)

    def test_deposition_file_operations(self):
        # Test data
        test_data = dict(
            metadata=dict(
                upload_type="presentation",
                title="Test title",
                creators=[
                    dict(name="Doe, John", affiliation="Atlantis"),
                    dict(name="Smith, Jane", affiliation="Atlantis")
                ],
                description="Test Description",
                publication_date="2013-05-08",
            )
        )

        # Create deposition
        response = self.post(
            'depositionlistresource',
            data=test_data,
            code=201,
        )
        data = response.json

        # Upload a file
        response = self.post(
            'depositionfilelistresource',
            urlargs=dict(resource_id=data['id']),
            is_json=False,
            data={'file': make_pdf_fixture('test.pdf'), 'name': 'test.pdf'},
            code=201,
        )
        self.assertEqual(response.json['filename'], 'test.pdf')
        self.assertTrue(response.json['id'])
        self.assertTrue(response.json['checksum'])
        self.assertTrue(response.json['filesize'])
        file_data = response.json

        # Upload another file
        response = self.post(
            'depositionfilelistresource',
            urlargs=dict(resource_id=data['id']),
            is_json=False,
            data={'file': make_pdf_fixture('test2.pdf'), 'name': 'test2.pdf'},
            code=201,
        )
        file_data2 = response.json

        # Upload another file with identical name
        response = self.post(
            'depositionfilelistresource',
            urlargs=dict(resource_id=data['id']),
            is_json=False,
            data={
                'file': make_pdf_fixture('test2.pdf', "test"),
                'name': 'test2.pdf'
            },
            code=400,
        )

        # Get file info
        response = self.get(
            'depositionfileresource',
            urlargs=dict(resource_id=data['id'], file_id=file_data['id']),
            code=200,
        )
        self.assertEqual(response.json, file_data)

        # Get non-existing file
        response = self.get(
            'depositionfileresource',
            urlargs=dict(resource_id=data['id'], file_id="bad_id"),
            code=404,
        )

        # Delete non-existing file
        response = self.delete(
            'depositionfileresource',
            urlargs=dict(resource_id=data['id'], file_id="bad_id"),
            code=404,
        )

        # Get list of files
        response = self.get(
            'depositionfilelistresource',
            urlargs=dict(resource_id=data['id'],),
            code=200,
        )
        self.assertEqual(len(response.json), 2)

        invalid_files_list = map(
            lambda x: {'filename': x['filename']},
            response.json
        )
        id_files_list = map(lambda x: {'id': x['id']}, response.json)
        id_files_list.reverse()

        # Sort files - invalid query
        response = self.put(
            'depositionfilelistresource',
            urlargs=dict(resource_id=data['id'],),
            data=invalid_files_list,
            code=400,
        )

        # Sort files - valid query
        response = self.put(
            'depositionfilelistresource',
            urlargs=dict(resource_id=data['id'],),
            data=id_files_list,
            code=200,
        )
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json[0]['id'], id_files_list[0]['id'])
        self.assertEqual(response.json[1]['id'], id_files_list[1]['id'])

        # Delete a file
        response = self.delete(
            'depositionfileresource',
            urlargs=dict(resource_id=data['id'], file_id=file_data['id']),
            code=204,
        )

        # Get list of files
        response = self.get(
            'depositionfilelistresource',
            urlargs=dict(resource_id=data['id']),
            code=200,
        )
        self.assertEqual(len(response.json), 1)

        # Rename file
        response = self.put(
            'depositionfileresource',
            urlargs=dict(resource_id=data['id'], file_id=file_data2['id']),
            data=dict(filename="another_test.pdf"),
            code=200,
        )
        self.assertEqual(file_data2['id'], response.json['id'])
        self.assertEqual(response.json['filename'], "another_test.pdf")

        # Bad renaming
        test_cases = [
            dict(name="another_test.pdf"),
            dict(filename="../../etc/passwd"),
        ]
        for test_case in test_cases:
            response = self.put(
                'depositionfileresource',
                urlargs=dict(resource_id=data['id'], file_id=file_data2['id']),
                data=test_case,
                code=400,
            )

        # Delete resource again
        response = self.delete(
            'depositionresource',
            urlargs=dict(resource_id=data['id'],),
            code=204
        )

        # No files any more
        response = self.get(
            'depositionfilelistresource',
            urlargs=dict(resource_id=data['id'],),
            code=404,
        )

    def test_delete(self):
        # Test data
        test_data = dict(
            metadata=dict(
                upload_type="presentation",
                title="Test title",
                creators=[
                    dict(name="Doe, John", affiliation="Atlantis"),
                    dict(name="Smith, Jane", affiliation="Atlantis")
                ],
                description="Test Description",
                publication_date="2013-05-08",
            )
        )

        # Create deposition
        response = self.post(
            'depositionlistresource', data=test_data, code=201,
        )
        res_id1 = response.json['id']

        # Create deposition
        response = self.post(
            'depositionlistresource', data=test_data, code=201,
        )
        res_id2 = response.json['id']

        self.get(
            'depositionresource', urlargs=dict(resource_id=res_id1), code=200
        )
        self.get(
            'depositionresource', urlargs=dict(resource_id=res_id2), code=200
        )

        # Delete one
        response = self.delete(
            'depositionresource',
            urlargs=dict(resource_id=res_id2),
            code=204
        )
        # Get the other
        self.get(
            'depositionresource', urlargs=dict(resource_id=res_id1), code=200
        )

    def test_depositions_non_existing(self):
        # Get non-existing
        response = self.get(
            'depositionresource',
            urlargs=dict(resource_id=-1,),
            code=404
        )
        self.assertTrue(response.json['message'])
        self.assertEqual(response.json['status'], 404)

        # Delete non-existing
        response = self.delete(
            'depositionresource',
            urlargs=dict(resource_id=-1,),
            code=404
        )
        self.assertTrue(response.json['message'])
        self.assertEqual(response.json['status'], 404)

    def test_bad_media_type(self):
        self.post(
            'depositionlistresource',
            data=dict(metadata=dict()),
            code=415,
            headers=[],
        )

        self.put(
            'depositionresource',
            urlargs=dict(resource_id=-1,),
            data=dict(metadata=dict()),
            code=415,
            headers=[],
        )

        self.put(
            'depositiondraftresource',
            urlargs=dict(resource_id=1, draft_id=1),
            data=dict(),
            code=415,
            headers=[],
        )

        self.post(
            'depositionfilelistresource',
            urlargs=dict(resource_id=1),
            data=dict(),
            code=415,
            headers=[],
        )

        self.put(
            'depositionfilelistresource',
            urlargs=dict(resource_id=1),
            data=dict(),
            code=415,
            headers=[],
        )

        self.put(
            'depositionfileresource',
            urlargs=dict(resource_id=1, file_id=1),
            data=dict(),
            code=415,
            headers=[],
        )

    def test_method_not_allowed(self):
        """ Ensure that methods return 405 """
        from flask import url_for
        tests = dict(
            depositionlistresource=(
                ['put', 'patch', 'head', 'options', 'delete', 'trace'],
                {}
            ),
            depositionresource=(
                ['post', 'patch', 'head', 'options', 'trace'],
                {'resource_id': -1}
            ),
            depositiondraftlistresource=(
                ['put', 'delete', 'post', 'patch', 'head', 'options', 'trace'],
                {'resource_id': -1}
            ),
            depositiondraftresource=(
                ['post', 'head', 'patch', 'options', 'trace'],
                {'resource_id': -1, 'draft_id': -1}
            ),
            depositionactionresource=(
                ['put', 'delete', 'get', 'patch', 'head', 'options', 'trace'],
                {'resource_id': -1, 'action_id': 'run'}
            ),
            depositionfilelistresource=(
                ['delete', 'patch', 'head', 'options', 'trace'],
                {'resource_id': -1}
            ),
            depositionfileresource=(
                ['post', 'patch', 'head', 'options', 'trace'],
                {'resource_id': -1, 'file_id': -1}
            ),
        )

        for endpoint, methods in tests.items():
            for m in methods[0]:
                request_func = getattr(self.client, m)
                response = request_func(
                    url_for(
                        endpoint,
                        access_token=self.accesstoken[self.user.id],
                        **methods[1]
                    ),
                    base_url=self.app.config['CFG_SITE_SECURE_URL'],
                )
                self.assertStatus(response, 405)

        allmethods = [
            'get', 'put', 'delete', 'post', 'patch', 'head', 'options', 'trace'
        ]

        for m in allmethods:
            for endpoint, methods in tests.items():
                if m not in methods[0]:
                    request_func = getattr(self.client, m)
                    response = request_func(
                        url_for(
                            endpoint,
                            **methods[1]
                        ),
                        base_url=self.app.config['CFG_SITE_SECURE_URL'],
                    )
                    self.assertStatus(response, 401)
                    self.assertEqual(
                        response.headers['Content-Type'],
                        "application/json"
                    )
                    self.assertEqual(response.json['status'], 401)


class WebDepositZenodoApiTest(DepositApiTestCase):
    resource_schema = dict(
        files=dict(type="list", required=True),
        created=dict(type="string", required=True),
        modified=dict(type="string", required=True),
        state=dict(
            type="string",
            allowed=['done', 'error', 'inprogress', ],
            required=True
        ),
        owner=dict(type="integer", required=True),
        id=dict(type="integer", required=True),
        title=dict(type="string", required=True),
        metadata=dict(type="dict", required=True),
        submitted=dict(type="boolean", required=True),
        record_id=dict(type="integer"),
        record_url=dict(type="string"),
        doi=dict(type="string"),
        doi_url=dict(type="string"),
    )
    metadata_schema = dict(
        access_right=dict(
            type='string',
            allowed=['open', 'closed', 'embargoed', 'restricted'],
        ),
        access_conditions=dict(type='string', nullable=True),
        communities=dict(type='list'),
        conference_acronym=dict(type='string'),
        conference_dates=dict(type='string'),
        conference_place=dict(type='string'),
        conference_title=dict(type='string'),
        conference_url=dict(type='string'),
        conference_session=dict(type='string'),
        conference_session_part=dict(type='string'),
        creators=dict(type='list', schema=dict(
            type='dict', schema=dict(
                name=dict(type='string'),
                affiliation=dict(type='string'),
                orcid=dict(type='string', nullable=True),
                gnd=dict(type='string', nullable=True),
            )
        )),
        description=dict(type='string'),
        doi=dict(type='string'),
        embargo_date=dict(type='string', nullable=True),
        grants=dict(type='list', schema=dict(
            type="dict", schema=dict(
                id=dict(type='string'),
                acronym=dict(type='string'),
                title=dict(type='string'),
            )
        )),
        image_type=dict(type='string'),
        imprint_isbn=dict(type='string'),
        imprint_place=dict(type='string'),
        imprint_publisher=dict(type='string'),
        journal_issue=dict(type='string'),
        journal_pages=dict(type='string'),
        journal_title=dict(type='string'),
        journal_volume=dict(type='string'),
        keywords=dict(type='list'),
        subjects=dict(type='list'),
        license=dict(type='string', nullable=True),
        notes=dict(type='string'),
        partof_pages=dict(type='string'),
        partof_title=dict(type='string'),
        prereserve_doi=dict(type='dict', nullable=True, schema=dict(
            doi=dict(type='string'),
            recid=dict(type='integer'),
        )),
        publication_date=dict(type='string'),
        publication_type=dict(type='string'),
        related_identifiers=dict(type='list', schema=dict(
            type='dict', schema=dict(
                identifier=dict(type='string'),
                relation=dict(type='string'),
                scheme=dict(type='string'),
            )
        )),
        references=dict(type='list', schema=dict(type='string')),
        thesis_supervisors=dict(type='list', schema=dict(
            type='dict', schema=dict(
                name=dict(type='string'),
                affiliation=dict(type='string'),
                orcid=dict(type='string', nullable=True),
                gnd=dict(type='string', nullable=True),
            )
        )),
        thesis_university=dict(type='string'),
        contributors=dict(type='list', schema=dict(
            type='dict', schema=dict(
                name=dict(type='string'),
                affiliation=dict(type='string'),
                type=dict(type='string'),
                orcid=dict(type='string', nullable=True),
                gnd=dict(type='string', nullable=True),
            )
        )),
        title=dict(type='string'),
        upload_type=dict(type='string'),
        recid=dict(type='integer', nullable=True),
        modification_date=dict(type='string', nullable=True),
    )

    def setUp(self):
        super(WebDepositZenodoApiTest, self).setUp()
        # Setup a test community
        from invenio.modules.communities.models import Community
        from invenio.ext.sqlalchemy import db
        # userb from zenodo.demosite.fixtures.accounts
        self.test_community_remove = False
        self.test_community = Community.query.filter_by(id='cfa').first()
        if not self.test_community:
            self.test_community = Community(
                id='cfa', title='Test Community', id_user=4
            )
            self.test_community_remove = True
            db.session.add(self.test_community)
            db.session.commit()

        self.test_community.save_collections()

    def tearDown(self):
        super(WebDepositZenodoApiTest, self).tearDown()
        if self.test_community_remove:
            self.test_community.delete_collections()
            db.session.delete(self.test_community)
            db.session.commit()

    def get_test_data(self, **extra):
        test_data = dict(
            metadata=dict(
                upload_type="presentation",
                title="Test title",
                creators=[
                    dict(name="Doe, John", affiliation="Atlantis"),
                    dict(name="Smith, Jane", affiliation="Atlantis")
                ],
                description="Test Description",
                publication_date="2013-05-08",
            )
        )
        test_data['metadata'].update(extra)
        return test_data

    def run_task_id(self, task_id):
        """ Run a bibsched task """
        import os
        from invenio.modules.scheduler.models import SchTASK
        CFG_BINDIR = self.app.config['CFG_BINDIR']

        bibtask = SchTASK.query.filter(SchTASK.id == task_id).first()
        assert bibtask is not None
        assert bibtask.status == 'WAITING'

        cmd = "%s/%s %s" % (CFG_BINDIR, bibtask.proc, task_id)
        assert not os.system(cmd)

    def run_tasks(self, alias=None):
        """
        Run all background tasks matching parameters
        """
        from invenio.modules.scheduler.models import SchTASK

        q = SchTASK.query
        if alias:
            q = q.filter(SchTASK.user == alias, SchTASK.status == 'WAITING')

        for r in q.all():
            self.run_task_id(r.id)

    def run_deposition_tasks(self, deposition_id, with_webcoll=True):
        # Run submitted tasks
        from invenio.modules.deposit.models import Deposition
        dep = Deposition.get(deposition_id)
        sip = dep.get_latest_sip(sealed=True)
        for task_id in sip.task_ids:
            self.run_task_id(task_id)

        if with_webcoll:
            # Run webcoll (to ensure record is assigned permissions)
            from invenio.legacy.bibsched.bibtask import \
                task_low_level_submission
            task_id = task_low_level_submission('webcoll', 'webdeposit', '-q')
            self.run_task_id(task_id)

            # Check if record is accessible
            response = self.client.get(
                url_for('record.metadata', recid=sip.metadata['recid']),
                base_url=self.app.config['CFG_SITE_SECURE_URL'],
            )
            self.assertStatus(response, 200)

    def assert_error(self, field, response):
        for e in response.json['errors']:
            if e.get('field') == field:
                return
        raise AssertionError("Field %s not found in errors" % field)

    def assert_workflow_status(self, res_id, obj_version, wf_status):
        from invenio.modules.workflows.models import BibWorkflowObject

        wfobj = BibWorkflowObject.query.filter_by(id=res_id).first()
        if obj_version is not None:
            self.assertEqual(wfobj.version, obj_version)
        if wf_status is not None:
            self.assertEqual(wfobj.workflow.status, wf_status)

    def test_input_output(self):
        test_data = dict(
            metadata=dict(
                access_right='embargoed',
                communities=[{'identifier': 'cfa'}],
                conference_acronym='Some acronym',
                conference_dates='Some dates',
                conference_place='Some place',
                conference_title='Some title',
                conference_url='http://someurl.com',
                conference_session='VI',
                conference_session_part='1',
                creators=[
                    dict(name="Doe, John", affiliation="Atlantis",
                         orcid="0000-0002-1825-0097", gnd="170118215"),
                    dict(name="Smith, Jane", affiliation="Atlantis")
                ],
                description="Some description",
                doi="10.1234/foo.bar",
                embargo_date="2010-12-09",
                grants=[dict(id="283595"), ],
                imprint_isbn="Some isbn",
                imprint_place="Some place",
                imprint_publisher="Some publisher",
                journal_issue="Some issue",
                journal_pages="Some pages",
                journal_title="Some journal name",
                journal_volume="Some volume",
                keywords=["Keyword 1", "keyword 2"],
                subjects=[
                    dict(scheme="gnd", identifier="1234567899", term="Astronaut"),
                    dict(scheme="gnd", identifier="1234567898", term="Amish"),
                ],
                license="cc-zero",
                notes="Some notes",
                partof_pages="SOme part of",
                partof_title="Some part of title",
                prereserve_doi=True,
                publication_date="2013-09-12",
                publication_type="book",
                references=[
                    "Reference 1",
                    "Reference 2",
                ],
                related_identifiers=[
                    dict(identifier='10.1234/foo.bar2', relation='isCitedBy'),
                    dict(identifier='10.1234/foo.bar3', relation='cites'),
                    dict(
                        identifier='2011ApJS..192...18K',
                        relation='isAlternativeIdentifier'),
                ],
                thesis_supervisors=[
                    dict(name="Doe Sr., John", affiliation="Atlantis"),
                    dict(name="Smith Sr., Jane", affiliation="Atlantis",
                         orcid="http://orcid.org/0000-0002-1825-0097",
                         gnd="http://d-nb.info/gnd/170118215")
                ],
                thesis_university="Some thesis_university",
                contributors=[
                    dict(name="Doe Sr., Jochen", affiliation="Atlantis",
                         type="Other"),
                    dict(name="Smith Sr., Marco", affiliation="Atlantis",
                         orcid="http://orcid.org/0000-0002-1825-0097",
                         gnd="http://d-nb.info/gnd/170118215",
                         type="DataCurator")
                ],
                title="Test title",
                upload_type="publication",
            )
        )

        response = self.post(
            'depositionlistresource', data=test_data, code=201,
        )
        v = Validator()
        if not v.validate(response.json, self.resource_schema):
            print v.errors
            raise AssertionError("Output does not validate according to schema")
        if not v.validate(response.json['metadata'], self.metadata_schema):
            print v.errors
            print response.json['metadata']
            raise AssertionError("Output does not validate according to schema")
        response = self.delete(
            'depositionresource',
            urlargs=dict(resource_id=response.json['id']),
            code=204,
        )

    def test_unicode(self):
        test_data = dict(
            metadata=dict(
                access_right='restricted',
                access_conditions='Αυτή είναι μια δοκιμή',
                communities=[{'identifier': 'cfa'}],
                conference_acronym='Αυτή είναι μια δοκιμή',
                conference_dates='هذا هو اختبار',
                conference_place='Սա փորձություն',
                conference_title='Гэта тэст',
                conference_url='http://someurl.com',
                conference_session='5',
                conference_session_part='a',
                creators=[
                    dict(name="Doe, John", affiliation="Това е тест"),
                    dict(name="Smith, Jane", affiliation="Tio ĉi estas testo")
                ],
                description="这是一个测试",
                doi="10.1234/foo.bar",
                embargo_date="2010-12-09",
                grants=[dict(id="283595"), ],
                imprint_isbn="Some isbn",
                imprint_place="這是一個測試",
                imprint_publisher="ეს არის გამოცდა",
                journal_issue="આ એક કસોટી છે",
                journal_pages="זהו מבחן",
                journal_title="यह एक परीक्षण है",
                journal_volume="Þetta er prófun",
                keywords=["これはテストです", "ಇದು ಪರೀಕ್ಷೆ"],
                subjects=[
                    dict(scheme="gnd", identifier="1234567899", term="これはです"),
                    dict(scheme="gnd", identifier="1234567898", term="ಇ"),
                ],
                license="cc-zero",
                notes="이것은 테스트입니다",
                partof_pages="ນີ້ແມ່ນການທົດສອບ",
                partof_title="ही चाचणी आहे",
                prereserve_doi=True,
                publication_date="2013-09-12",
                publication_type="book",
                related_identifiers=[
                    dict(
                        identifier='2011ApJS..192...18K',
                        relation='isAlternativeIdentifier'),
                    dict(identifier='10.1234/foo.bar2', relation='isCitedBy'),
                    dict(identifier='10.1234/foo.bar3', relation='cites'),
                ],
                thesis_supervisors=[
                    dict(name="Doe Sr., این یک تست است", affiliation="Atlantis"),
                    dict(name="Это Sr., Jane", affiliation="Atlantis")
                ],
                thesis_university="இந்த ஒரு சோதனை",
                contributors=[
                    dict(name="Doe Sr.,  ن یک تست", affiliation="Atlantis",
                         type="Other"),
                    dict(name="SmЭтith Sr., Marco", affiliation="Atlantis",
                         type="DataCurator")
                ],
                title="Đây là một thử nghiệm",
                upload_type="publication",
            )
        )

        response = self.post(
            'depositionlistresource', data=test_data, code=201,
        )
        res_id = response.json['id']
        v = Validator()
        if not v.validate(response.json, self.resource_schema):
            print v.errors
            raise AssertionError("Output does not validate according to schema")
        if not v.validate(response.json['metadata'], self.metadata_schema):
            print v.errors
            raise AssertionError("Output does not validate according to schema")

        # Upload 3 files
        for i in range(3):
            response = self.post(
                'depositionfilelistresource',
                urlargs=dict(resource_id=res_id),
                is_json=False,
                data={
                    'file': make_pdf_fixture('test%s.pdf' % i),
                    'name': 'test-%s.pdf' % i,
                },
                code=201,
            )

        from invenio.modules.workflows.engine import ObjectVersion, \
            WorkflowStatus
        self.assert_workflow_status(
            res_id, ObjectVersion.INITIAL, None
        )

        # Publish deposition
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='publish'),
            code=202
        )

        self.assert_workflow_status(
            res_id, ObjectVersion.COMPLETED, WorkflowStatus.COMPLETED
        )

        self.run_deposition_tasks(res_id)

    def test_malicious_data(self):
        test_data = dict(
            metadata=dict(
                communities=['harvard', ],
                #creators=["Doe, John", ],
                description="""<script type="text/javascript">alert('Malicious data');</script>""",
                title="Test title",
                upload_type="presentation",
            )
        )
        response = self.post(
            'depositionlistresource', data=test_data, code=400,
        )
        self.assert_error('communities', response)
        self.assert_error('description', response)

    def test_form_flags_issues(self):
        test_data = dict(
            metadata=dict(
                access_right='open',
                license='cc-by-sa',
                upload_type='dataset',
                title='Form flags issues',
                creators=[{'name': 'Lars', 'affiliation': 'CERN'}, ],
                description="Bla bla",
            )
        )
        response = self.post(
            'depositionlistresource', data=test_data, code=201,
        )
        m = response.json['metadata']
        self.assertEqual(m['license'], 'cc-by-sa')
        self.assertEqual(m['embargo_date'], None)

        test_data = dict(
            metadata=dict(
                access_right='closed',
                license='cc-by-sa',  # Not valid for closed access articles.
                upload_type='dataset',
                title='Form flags issues',
                creators=[{'name': 'Lars', 'affiliation': 'CERN'}, ],
                description="Bla bla",
            )
        )
        response = self.post(
            'depositionlistresource', data=test_data, code=201,
        )
        self.assertEqual(response.json['metadata']['license'], None)

    def test_pre_reserve_doi(self):
        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                prereserve_doi=True,
            ),
            code=201,
        )
        res_id = response.json['id']
        reserved_doi = response.json['metadata']['prereserve_doi']['doi']
        self.assertEqual(
            response.json['metadata']['prereserve_doi']['doi'],
            response.json['metadata']['doi']
        )
        self.assertTrue(
            response.json['metadata']['prereserve_doi']['doi'].endswith(
                str(response.json['metadata']['prereserve_doi']['recid'])
            )
        )
        response = self.put(
            'depositionresource', urlargs=dict(resource_id=res_id),
            data=self.get_test_data(
                prereserve_doi={'doi': '10.1234/foo.bar', 'recid': 1000},
            ),
            code=200
        )
        self.assertEqual(
            response.json['metadata']['prereserve_doi']['doi'],
            reserved_doi
        )

        response = self.delete(
            'depositionresource', urlargs=dict(resource_id=res_id), code=204
        )

    def test_related_identifiers(self):
        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                related_identifiers=[
                    {'identifier': 'doi:10.1234/foo.bar', 'relation': 'cites'},
                ],
            ),
            code=201,
        )
        res_id = response.json['id']
        rel = response.json['metadata']['related_identifiers'][0]
        self.assertEqual(rel['identifier'], '10.1234/foo.bar')
        self.assertEqual(rel['scheme'], 'doi')
        self.assertEqual(rel['relation'], 'cites')

        response = self.delete(
            'depositionresource', urlargs=dict(resource_id=res_id), code=204
        )

    def test_orcid(self):
        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                creators=[
                    {'name': 'Lars', 'affiliation': 'CERN',
                     'orcid': 'http://orcid.org/0000-0001-8135-3489'}
                ],
            ),
            code=201,
        )
        res_id = response.json['id']
        creator = response.json['metadata']['creators'][0]
        self.assertEqual(creator['orcid'], '0000-0001-8135-3489')

        response = self.delete(
            'depositionresource', urlargs=dict(resource_id=res_id), code=204
        )

    def test_gnd(self):
        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                creators=[
                    {'name': 'Lars', 'affiliation': 'CERN',
                     'gnd': 'http://d-nb.info/gnd/170118215'}
                ],
            ),
            code=201,
        )
        res_id = response.json['id']
        creator = response.json['metadata']['creators'][0]
        self.assertEqual(creator['gnd'], '170118215')

        response = self.delete(
            'depositionresource', urlargs=dict(resource_id=res_id), code=204
        )

    def test_grants(self):
        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                grants=[
                    {'id': 'invalid', },
                ],
            ),
            code=400,
        )

        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                grants=[
                    {'id': 283595, 'acronym': 'invalid', },
                ],
            ),
            code=201,
        )

        self.assertEqual(
            response.json['metadata']['grants'][0]['acronym'],
            'OPENAIREPLUS'
        )

    def test_validation(self):
        # Test utf8
        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                access_right='notvalid',
                conference_url='not_a_url',
                conference_dates='something to force conference_title and conference_acronym',
                conference_place='something to force conference_title and conference_acronym',
                doi="not a doi",
                embargo_date='not a date',
                license='not a license',
                publication_date='not a date',
                title='',
                upload_type='notvalid'
            ),
            code=400,
        )
        self.assert_error('access_right', response)
        self.assert_error('conference_url', response)
        self.assert_error('conference_title', response)
        self.assert_error('conference_acronym', response)
        self.assert_error('doi', response)
        self.assert_error('embargo_date', response)
        self.assert_error('license', response)
        self.assert_error('publication_date', response)
        self.assert_error('title', response)
        self.assert_error('upload_type', response)

        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                upload_type='image',
                image_type='not_an_image_type',
            ),
            code=400,
        )
        self.assert_error('image_type', response)

        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                upload_type='publication',
                image_type='not_an_publication_type',
            ),
            code=400,
        )
        self.assert_error('publication_type', response)

        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                communities=[{'identifier': 'invalid-identifier'}, ]
            ),
            code=400,
        )
        self.assert_error('communities', response)

        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                creators=[{'affiliation': 'TEST'}, ]
            ),
            code=400,
        )
        self.assert_error('creators', response)

        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                creators=[{'name': 'TEST', 'affiliation': 'TEST',
                           'orcid': 'INVALID'}, ]
            ),
            code=400,
        )
        self.assert_error('creators', response)

        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                creators=[{'name': 'TEST', 'affiliation': 'TEST',
                           'gnd': 'INVALID'}, ]
            ),
            code=400,
        )
        self.assert_error('creators', response)

        response = self.post(
            'depositionlistresource', data=self.get_test_data(
                description="""Test<script type="text/javascript">
                    alert("Hej");
                    </script>
                    """
            ),
            code=201,
        )
        self.assertTrue('<script' not in
                        response.json['metadata']['description'])

    def test_depositions_list_post_create_delete(self):
        # Test data
        test_data = dict(
            metadata=dict(
                upload_type="presentation",
                title="Test title",
                creators=[
                    dict(name="Doe, John", affiliation="Atlantis"),
                    dict(name="Smith, Jane", affiliation="Atlantis")
                ],
                description="Test Description",
                publication_date="2013-05-08",
            )
        )

        update_data = dict(
            metadata=dict(
                title="New test title",
            )
        )

        # Create deposition
        response = self.post(
            'depositionlistresource', data=test_data, code=201
        )

        self.assertTrue(response.json['id'])
        self.assertTrue(response.json['created'])
        self.assertTrue(response.json['modified'])
        self.assertEqual(response.json['files'], [])
        self.assertEqual(response.json['owner'], self.user.id)
        self.assertEqual(response.json['state'], 'inprogress')
        post_data = response.json

        # Get deposition again and compare
        response = self.get(
            'depositionresource',
            urlargs=dict(resource_id=post_data['id']),
            code=200
        )
        self.assertEqual(post_data, response.json)
        v = Validator()
        if v.validate(response.json, self.metadata_schema):
            raise AssertionError("Output does not validate according to schema")

        # Update deposition
        response = self.put(
            'depositionresource',
            urlargs=dict(resource_id=post_data['id']),
            data=update_data,
            code=200,
        )
        post_data['metadata']['title'] = update_data['metadata']['title']
        self.assertEqual(post_data['metadata'], response.json['metadata'])
        self.assertEqual(post_data['created'], response.json['created'])

        # Submit without files is not possible deposition
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=post_data['id'], action_id='publish'),
            code=400
        )

        # Delete resource again
        response = self.delete(
            'depositionresource',
            urlargs=dict(resource_id=post_data['id']),
            code=204,
        )

    def test_submit(self):
        test_data = dict(
            metadata=dict(
                upload_type="presentation",
                title="Test title",
                creators=[
                    dict(name="Doe, John", affiliation="Atlantis"),
                    dict(name="Smith, Jane", affiliation="Atlantis")
                ],
                description="Test Description",
                publication_date="2013-05-08",
            )
        )

        # Create deposition
        response = self.post(
            'depositionlistresource', data=test_data, code=201
        )
        res_id = response.json['id']

        # Upload 3 files
        for i in range(3):
            response = self.post(
                'depositionfilelistresource',
                urlargs=dict(resource_id=res_id),
                is_json=False,
                data={
                    'file': make_pdf_fixture('test%s.pdf' % i),
                    'name': 'test-%s.pdf' % i,
                },
                code=201,
            )

        # Publish deposition
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='publish'),
            code=202
        )

        #
        # Test for workflow status
        #
        from invenio.modules.workflows.engine import ObjectVersion, \
            WorkflowStatus
        self.assert_workflow_status(
            res_id, ObjectVersion.COMPLETED, WorkflowStatus.COMPLETED
        )

        # Second request will return forbidden since it's already published
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='publish'),
            code=400
        )

        # Not allowed to edit drafts
        response = self.put(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            data=test_data,
            code=403,
        )
        response = self.put(
            'depositiondraftresource',
            urlargs=dict(resource_id=res_id, draft_id='_default'),
            data=test_data,
            code=403,
        )

        # Not allowed to delete
        response = self.delete(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            code=403,
        )

        # Not allowed to sort files
        response = self.get(
            'depositionfilelistresource',
            urlargs=dict(resource_id=res_id,),
            code=200,
        )
        files_list = map(lambda x: {'id': x['id']}, response.json)
        files_list.reverse()
        response = self.put(
            'depositionfilelistresource',
            urlargs=dict(resource_id=res_id,),
            data=files_list,
            code=403,
        )

        # Not allowed to add files
        response = self.post(
            'depositionfilelistresource',
            urlargs=dict(resource_id=res_id),
            is_json=False,
            data={
                'file': make_pdf_fixture('test5.pdf'),
                'name': 'test-5.pdf',
            },
            code=403,
        )

        # Not allowed to delete file
        response = self.delete(
            'depositionfileresource',
            urlargs=dict(resource_id=res_id, file_id=files_list[0]['id']),
            code=403,
        )

        # Not allowed to rename file
        response = self.put(
            'depositionfileresource',
            urlargs=dict(resource_id=res_id, file_id=files_list[0]['id']),
            data=dict(filename="another_test.pdf"),
            code=403,
        )

        self.assert_workflow_status(
            res_id, ObjectVersion.COMPLETED, WorkflowStatus.COMPLETED
        )

        self.run_deposition_tasks(res_id)

    def test_edit(self):
        test_data = dict(
            metadata=dict(
                access_right='embargoed',
                embargo_date="2010-12-09",
                upload_type="publication",
                title="Test title",
                creators=[
                    dict(name="Doe, John", affiliation="Atlantis"),
                    dict(name="Smith, Jane", affiliation="Atlantis")
                ],
                description="<p>Test <em>Description</em></p>",
                publication_date="2013-05-08",
                communities=[{'identifier': 'cfa'}, ],
                grants=[dict(id="283595"), ],
                license="cc-zero",
                conference_acronym='Some acronym',
                conference_dates='Some dates',
                conference_place='Some place',
                conference_title='Some title',
                conference_url='http://someurl.com',
                conference_session='VI',
                conference_session_part='2',
                imprint_isbn="Some isbn",
                imprint_place="Some place",
                imprint_publisher="Some publisher",
                journal_issue="Some issue",
                journal_pages="Some pages",
                journal_title="Some journal name",
                journal_volume="Some volume",
                keywords=["Keyword 1", "keyword 2"],
                subjects=[
                    dict(scheme="gnd", identifier="1234567899", term="Astronaut"),
                    dict(scheme="gnd", identifier="1234567898", term="Amish"),
                ],
                notes="Some notes",
                partof_pages="SOme part of",
                partof_title="Some part of title",
                publication_type="book",
                related_identifiers=[
                    dict(
                        identifier='2011ApJS..192...18K',
                        relation='isAlternativeIdentifier'),
                    dict(identifier='10.1234/foo.bar2', relation='isCitedBy'),
                    dict(identifier='10.1234/foo.bar3', relation='cites'),
                ],
                thesis_supervisors=[
                    dict(name="Doe Sr., John", affiliation="Atlantis"),
                    dict(name="Smith Sr., Jane", affiliation="Atlantis")
                ],
                thesis_university="Some thesis_university",
                contributors=[
                    dict(name="Doe Sr., Jochen", affiliation="atlantis",
                         type="Other"),
                    dict(name="Smith Sr., Marco", affiliation="atlantis",
                         type="DataCurator")
                ],
            )
        )

        # Create deposition
        response = self.post(
            'depositionlistresource', data=test_data, code=201
        )
        res_id = response.json['id']
        initial_data = response.json['metadata']

        # Upload a file
        response = self.post(
            'depositionfilelistresource',
            urlargs=dict(resource_id=res_id),
            is_json=False,
            data={
                'file': make_pdf_fixture('test.pdf'),
                'name': 'test.pdf',
            },
            code=201,
        )

        # Edit deposition - not a valid action at this point.
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='edit'),
            code=400
        )

        # Discard changes - not a valid action at this point.
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='discard'),
            code=400
        )

        # Publish deposition
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='publish'),
            code=202
        )

        record_id = response.json['record_id']

        from invenio.modules.workflows.engine import ObjectVersion, \
            WorkflowStatus
        self.assert_workflow_status(
            res_id, ObjectVersion.COMPLETED, WorkflowStatus.COMPLETED
        )

        # Edit deposition - not possible yet (until fully integrated)
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='edit'),
            code=409
        )

        self.assert_workflow_status(
            res_id, ObjectVersion.WAITING, WorkflowStatus.HALTED
        )

        # Edit deposition - check for consistency in result being returned
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='edit'),
            code=409
        )

        # Integrate record.
        self.run_deposition_tasks(res_id, with_webcoll=True)

        # Edit deposition
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='edit'),
            code=201
        )

        self.assert_workflow_status(
            res_id, ObjectVersion.WAITING, WorkflowStatus.HALTED
        )

        # Edit deposition - second request should return bad request (state of
        # of resource changed).
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='edit'),
            code=400
        )

        # Validate loaded metadata
        response = self.get(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            code=200
        )
        edit_data = response.json['metadata']
        self.assertTrue(edit_data['doi'])
        # Remove differences between edit metadata and new metadata
        del initial_data['prereserve_doi']
        del initial_data['doi']
        del edit_data['doi']
        self.assertEqual(edit_data, initial_data)

        # Not allowed to delete
        response = self.delete(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            code=403,
        )

        # Update deposition
        response = self.put(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            data=dict(metadata=dict(
                title="My new title",
                creators=[
                    dict(name="Smith, Jane", affiliation="Atlantis"),
                    dict(name="Doe, John", affiliation="Atlantis"),
                ],
                access_right="closed",
                thesis_supervisors=[
                    dict(name="Doe Jr., John", affiliation="Atlantis"),
                    dict(name="Smith Sr., Jane", affiliation="CERN"),
                    dict(name="Doe Sr., John", affiliation="CERN"),
                ],
                contributors=[
                    dict(name="Doe Jr., Jochen", affiliation="Atlantis",
                         type="Other"),
                    dict(name="Smith Sr., Marco", affiliation="CERN",
                         type="DataCurator"),
                    dict(name="Doe Sr., Jochen", affiliation="CERN",
                         type="Other"),
                ],
            )),
            code=200,
        )
        self.assertEqual(response.json['metadata']['title'], "My new title")

        # Update deposition - cannot change doi
        response = self.put(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            data=dict(metadata=dict(
                doi="10.5072/zenodo.1234",
            )),
            code=400,
        )

        self.assert_workflow_status(
            res_id, ObjectVersion.WAITING, WorkflowStatus.HALTED
        )

        # Update deposition - cannot edit recid and modification_date (hidden)
        response = self.put(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            data=dict(metadata=dict(
                modification_date="2013-11-27 07:46:14",
                recid=10,
            )),
            code=400,
        )
        self.assertEqual(len(response.json['errors']), 2)
        self.assertEqual(
            response.json['errors'],
            [
                {'field': 'recid', 'message': 'unknown field', 'code': 10},
                {'field': 'modification_date', 'message': 'unknown field',
                 'code': 10}
            ]
        )

        # Get deposition metadata
        response = self.get(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            code=200,
        )
        self.assertNotEqual(
            response.json['metadata']['doi'],
            "10.5072/zenodo.1234"
        )

        # File restrictions
        # - check file availability before changing to closed access
        # - i.e. file is accessible to public
        response = self.client.get(
            url_for('record.files', recid=record_id) + "/test.pdf"
        )
        self.assertStatus(response, 200)

        #
        # Approve record in community - to test record merging
        #
        from invenio.modules.communities.models import Community
        u = Community.query.filter_by(id='zenodo').first()
        u.accept_record(record_id)
        self.run_tasks(alias='community')

        # Publish edited deposition
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='publish'),
            code=202
        )

        self.assert_workflow_status(
            res_id, ObjectVersion.COMPLETED, WorkflowStatus.COMPLETED
        )

        # Edit deposition - not possible yet (until fully integrated)
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='edit'),
            code=409
        )

        self.assert_workflow_status(
            res_id, ObjectVersion.WAITING, WorkflowStatus.HALTED
        )

        # Integrate record
        self.run_deposition_tasks(res_id, with_webcoll=True)

        # Check record
        from invenio.modules.records.api import get_record
        record = get_record(record_id, reset_cache=True)
        self.assertEqual(record['title'], "My new title")
        self.assertEqual(record['access_right'], "closed")
        self.assertEqual(record['authors'], [
            dict(name="Smith, Jane", affiliation="Atlantis", gnd='', orcid='',
                 familyname="Smith", givennames="Jane"),
            dict(name="Doe, John", affiliation="Atlantis", gnd='', orcid='',
                 familyname="Doe", givennames="John"),
        ])
        self.assertEqual(record['thesis_supervisors'], [
            dict(name="Doe Jr., John", affiliation="Atlantis", gnd='',
                 orcid=''),
            dict(name="Smith Sr., Jane", affiliation="CERN", gnd='', orcid=''),
            dict(name="Doe Sr., John", affiliation="CERN", gnd='', orcid=''),
        ])
        self.assertEqual(record['contributors'], [
            dict(name="Doe Jr., Jochen", affiliation="Atlantis", type='Other',
                 gnd='', orcid=''),
            dict(name="Smith Sr., Marco", affiliation="CERN",
                 type='DataCurator', gnd='', orcid=''),
            dict(name="Doe Sr., Jochen", affiliation="CERN", type='Other',
                 gnd='', orcid=''),
        ])
        self.assertEqual(record.get('embargo_date'), None)
        self.assertEqual(record.get('license'), None)
        self.assertEqual(record['owner']['deposition_id'], str(res_id))
        self.assertEqual(record.get('url'), None)
        self.assertEqual(record['alternate_identifiers'][0]['scheme'], "ads")

        # Communities
        self.assertEqual(record.get('communities'), ['zenodo'])
        self.assertEqual(
            record.get('provisional_communities'),
            ['cfa', 'ecfunded']
        )

        # File restrictions
        # - check file availability after changing to closed access
        # - file *is* accessible by uploader.
        response = self.client.get(
            url_for('record.files', recid=record_id) + "/test.pdf"
        )
        self.assertStatus(response, 200)
        # - file *is not* publicly accessible.
        self.logout()
        response = self.client.get(
            url_for('record.files', recid=record_id) + "/test.pdf"
        )
        self.assertStatus(response, 404)


        # Edit deposition - now possible again
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='edit'),
            code=201
        )

        # Update deposition
        response = self.put(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            data=dict(metadata=dict(
                title="To be discarded",
            )),
            code=200,
        )

        # Get deposition metadata
        response = self.get(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            code=200,
        )
        self.assertEqual(
            response.json['metadata']['title'],
            "To be discarded"
        )
        # Test if alternate identifiers was loaded correctly.
        self.assertEqual(
            response.json['metadata']['related_identifiers'][0],
            {u'scheme': u'ads', u'identifier': u'2011ApJS..192...18K',
             u'relation': u'isAlternativeIdentifier'},
        )

        # Discard changes.
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='discard'),
            code=201
        )

        self.assert_workflow_status(
            res_id, ObjectVersion.COMPLETED, WorkflowStatus.COMPLETED
        )

        # Discard changes - state of resource changed (no longer a valid
        # action)
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='discard'),
            code=400
        )

        # Get deposition metadata
        response = self.get(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            code=200,
        )
        self.assertEqual(
            response.json['metadata']['title'],
            "My new title"
        )

    def _create_and_upload(self, extra=None, webcoll=False):
        test_data = dict(
            metadata=dict(
                access_right='open',
                upload_type="dataset",
                title="Test empty edit",
                creators=[
                    dict(name="Doe, John", affiliation="Atlantis"),
                    dict(name="Smith, Jane", affiliation="Atlantis")
                ],
                description="<p>Test <em>Description</em></p>",
                license="cc-by-sa",
            )
        )

        if extra is not None:
            test_data['metadata'].update(extra)

        # Create deposition
        response = self.post(
            'depositionlistresource', data=test_data, code=201
        )
        res_id = response.json['id']

        # Upload a file
        response = self.post(
            'depositionfilelistresource',
            urlargs=dict(resource_id=res_id),
            is_json=False,
            data={
                'file': make_pdf_fixture('test.pdf'),
                'name': 'test.pdf',
            },
            code=201,
        )

        # Publish deposition
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='publish'),
            code=202
        )
        self.run_deposition_tasks(res_id, with_webcoll=webcoll)

        return res_id

    def test_file_restrictions(self):
        extra_data = dict(
            access_right='embargoed',
            embargo_date=(date.today() + timedelta(days=2)).isoformat()
        )

        # Reset certain legacy module level caches which are not being reset
        # properly when certain tests during a single testrun are creating
        # restricted collections.
        from invenio.legacy.search_engine import restricted_collection_cache, \
            collection_reclist_cache
        restricted_collection_cache.recreate_cache_if_needed()
        collection_reclist_cache.recreate_cache_if_needed()

        res_id = self._create_and_upload(extra=extra_data, webcoll=True)

        # Get deposition
        response = self.get(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            code=200
        )
        record_id = response.json['record_id']


        response = self.client.get(
            url_for('record.files', recid=record_id) + "/test.pdf"
        )
        self.assertStatus(response, 404)

    def test_missing_file(self):
        # Test data
        test_data = dict(
            metadata=dict(
                upload_type="presentation",
                title="Test title",
                creators=[
                    dict(name="Doe, John", affiliation="Atlantis"),
                    dict(name="Smith, Jane", affiliation="Atlantis")
                ],
                description="Test Description",
                publication_date="2013-05-08",
            )
        )

        # Create deposition
        response = self.post(
            'depositionlistresource',
            data=test_data,
            code=201,
        )
        res_id = response.json['id']

        # Publish edited deposition (missing file)
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='publish'),
            code=400
        )

        self.assertTrue(response.json['message'])
        self.assertTrue(response.json['errors'])
        self.assertEqual(response.json['status'], 400)
        self.assertEqual(len(response.json['errors']), 1)
        self.assertEqual(
            response.json['errors'][0],
            dict(message="Minimum one file must be provided.", code=10)
        )

    def test_empty_edit(self):
        """
        Test case when uploaded record has no changes, causing version id of
        the record to be unmodified, which can cause the upload not to be
        present.
        """
        res_id = self._create_and_upload()

        # Edit deposition
        self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='edit'),
            code=201
        )

        # Publish edited deposition (no modifications made)
        self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='publish'),
            code=202
        )
        self.run_deposition_tasks(res_id, with_webcoll=False)

        # Edit deposition - should be possible.
        self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='edit'),
            code=201
        )

    def test_marshalling(self):
        """
        """
        res_id = self._create_and_upload()

        expected_marshal = {
            u'access_right': u'open',
            u'access_conditions': None,
            u'communities': [],
            u'conference_acronym': None,
            u'conference_dates': None,
            u'conference_place': None,
            u'conference_title': None,
            u'conference_url': None,
            u'conference_session': None,
            u'conference_session_part': None,
            u'creators': [
                {u'affiliation': u'Atlantis', u'name': u'Doe, John',
                 u'gnd': u'', u'orcid': u''},
                {u'affiliation': u'Atlantis', u'name': u'Smith, Jane',
                 u'gnd': u'', u'orcid': u''},
            ],
            u'description': u'<p>Test <em>Description</em></p>',
            u'embargo_date': None,
            u'grants': [],
            u'image_type': u'',
            u'imprint_isbn': None,
            u'imprint_place': None,
            u'imprint_publisher': None,
            u'journal_issue': None,
            u'journal_pages': None,
            u'journal_title': None,
            u'journal_volume': None,
            u'keywords': [],
            u'subjects': [],
            u'license': u'cc-by-sa',
            u'notes': u'',
            u'partof_pages': None,
            u'partof_title': None,
            u'publication_date': u'%s' % date.today().isoformat(),
            u'publication_type': u'',
            u'related_identifiers': [],
            u'references': [],
            u'thesis_supervisors': [],
            u'contributors': [],
            u'title': u'Test empty edit',
            u'upload_type': u'dataset'
        }

        # Get marshalling via record
        response = self.get(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            code=200
        )
        record_marshal = response.json['metadata']
        import copy
        record_marshal_test = copy.copy(record_marshal)
        del record_marshal_test['doi']
        self.assertEqual(record_marshal_test, expected_marshal)

        # Edit deposition
        response = self.post(
            'depositionactionresource',
            urlargs=dict(resource_id=res_id, action_id='edit'),
            code=201
        )

        # Get marshalling via a loaded drafts
        response = self.get(
            'depositionresource',
            urlargs=dict(resource_id=res_id),
            code=200
        )
        draft_marshal = response.json['metadata']

        self.assertEqual(record_marshal['license'], 'cc-by-sa')
        self.assertEqual(draft_marshal['license'], 'cc-by-sa')
        self.assertEqual(record_marshal, draft_marshal)


TEST_SUITE = make_test_suite(
    WebDepositApiTest,
    WebDepositZenodoApiTest
)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
