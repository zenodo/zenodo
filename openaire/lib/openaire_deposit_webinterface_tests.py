# -*- encoding: utf8 -*-
## This file is part of Invenio.
## Copyright (C) 2010, 2011, 2012 CERN.
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
TODO: Strong dependency on Werkzeug and json
"""

from StringIO import StringIO
from tempfile import mkstemp
try:
    import json
except ImportError:
    import simplejson as json
import os
import re
import unittest

from invenio.bibrecord import record_add_field, record_xml_output
from invenio.bibtask import task_low_level_submission
from invenio.config import CFG_PREFIX
from invenio.dbquery import run_sql
from invenio.openaire_deposit_checks import CFG_METADATA_FIELDS_CHECKS
from invenio.openaire_deposit_config import CFG_METADATA_FIELDS
from invenio.openaire_deposit_engine import OpenAIREPublication
from invenio.openaire_deposit_fixtures import FIXTURES
from invenio.openaire_deposit_webinterface import \
    WebInterfaceOpenAIREDepositPages
from invenio.testutils import make_test_suite, run_test_suite
from invenio.testutils_clients import RequestFactory, TestClient, JSONResponse
from invenio.webuser import get_nickname


# TODO: only works in 2.7

class SubmissionRegressionTest(unittest.TestCase):
    # ================================
    # Tests
    # ================================
    def setUp(self):
        """
        Create test client, login with the given user and create a new publication.
        """
        self.client = TestClient()
        self.client.login('admin', '')

    def tearDown(self):
        """
        Remove the publication again.
        """
        self.client = None

    def test_load_old_submission(self):
        """
        Test that an old submission can be properly loaded, even if not all metadata is there.
        """
        response = self.client.get("/deposit", query_string={'projectid':
                                   '246686', 'ln': 'en', 'style': 'invenio'})
        self.assertEqual(response.status_code, 200)

    def test_noflash_nofileupload(self):
        """
        Test that hitting "Upload" without attaching a file does not
        result in a Internal Server Error
        """
        response = self.client.post(
            "/deposit",
            query_string={'projectid': '0', 'ln': 'en', 'style': 'invenio'},
            data={
                'upload': 'Upload',
                'Filedata': (StringIO(''), ''),
            }
        )
        self.assertNotEqual(response.status_code, 500)
        response = self.client.post(
            "/deposit",
            query_string={'projectid': '0', 'ln': 'en', 'style': 'invenio'},
            data={
                'upload': 'Upload',
                'Filedata': (StringIO(''), ''),
            }
        )
        self.assertNotEqual(response.status_code, 500)


class AjaxGatewayTest(unittest.TestCase):
    """
    Testing of AJAX Gateway
    """

    user_id = None
    """ User for which we want to add publications. """

    project_id = '283595'

    test_full_submit = True
    """ Set to True if you want to test full submission. By default this
    is not enabled, since it will pollute your installation.
    """

    # ================================
    # Helpers
    # ================================
    def _base_form(self, action='', projectid='0', current_field='', data={}, override_pubid=None):
        """
        Helper for creating required POST form parameters

        @param action: Name of action (e.g. save, submit, verify_field, ...)
        @param projectid: Id of project, can be left empty (defaults to NOPROJECT).
        @param current_field: Name of the current field without publication id suffix (e.g. language).
        @param data: Dictionary of fields/values for the form (without publication id suffix)/
        """
        pub_id = override_pubid or self.pub_id

        form = {}
        for field in CFG_METADATA_FIELDS:
            form['%s_%s' % (field, pub_id)] = ''

        if current_field:
            current_field_pub_id = ('%s_%s' % (current_field, pub_id))
        else:
            current_field_pub_id = ''

        form.update({
            'projectid': projectid,
            'publicationid': pub_id,
            'action': action,
            'current_field': current_field_pub_id,
            'save_%s' % pub_id: "Save+publication",
            'submit_%s' % pub_id: "Submit+publication",

        })

        # Default form values
        form.update({
            'publication_type_%s' % pub_id: 'publishedArticle',
            'access_rights_%s' % pub_id: 'openAccess',
            'language_%s' % pub_id: 'eng',
        })

        # Add form data
        for k, v in data.items():
            form['%s_%s' % (k, pub_id)] = v

        return form

    #
    # Actions
    #
    def action_verify_field(self, field, value, extra_data={}, **kwargs):
        """ Helper for creating required POST parameters for verify_field action """
        data = {field: value}
        data.update(extra_data)
        return self._base_form(
            action='verify_field',
            current_field=field,
            data=data,
            **kwargs
        )

    def action_save(self, data={}, **kwargs):
        """ Helper for creating required POST parameters for save action """
        return self._base_form(
            action='save',
            current_field='save',
            data=data,
            **kwargs
        )

    def action_submit(self, data={}, **kwargs):
        """ Helper for creating required POST parameters for save action """
        return self._base_form(
            action='submit',
            current_field='submit',
            data=data,
            **kwargs
        )

    #
    # Utility methods
    #
    def make_stringio_pdf(self, text):
        """
        Generate a PDF which includes the text given as parameter to this function.
        """
        from reportlab.pdfgen import canvas

        output = StringIO()

        c = canvas.Canvas(output)
        c.drawString(100, 100, text)
        c.showPage()
        c.save()

        return output.getvalue()

    def get_publications_for_project(self, project_id, style='invenio'):
        """ Get all publications for a project """
        RE_DELETE_LINK = re.compile("/deposit\?projectid=%s&amp;delete=([a-z0-9]+)&amp;ln=" % project_id, re.IGNORECASE)
        resp = self.client.get("/deposit", query_string={'style':
                               style, 'ln': 'en', 'projectid': project_id})
        return filter(lambda x: x != self.pub_id, RE_DELETE_LINK.findall(resp.data))  # Filter out pub from setUp

    def clear_publications(self, project_id, style='invenio'):
        """ Clear all publications for a project """
        pub_ids = self.get_publications_for_project(project_id, style=style)
        for pub_id in pub_ids:
            resp = self.client.get("/deposit", query_string={'projectid':
                                   project_id, 'delete': pub_id, 'ln': ''})
            self.assertEqual(resp.status_code, 200)

    def save_metadata(self, project_id, pub_id, fixture):
        """ Load a fixture and save it for the given publication """
        res = self.client.post("/deposit/ajaxgateway", data=self.action_save(
            data=fixture, override_pubid=pub_id, projectid=project_id))
        for field, error in res.json['errors'].items():
            self.assertEqual(error, '', msg="Save unsuccessful - %s error: %s" % (field, error))
        self.assertPublicationMetadata(pub_id, fixture)

    def approve_record(self, recid):
        """ Approve a record to make it publicly available """
        # Make MARCXML to approve record
        rec = {}
        record_add_field(rec, '001', controlfield_value=str(recid))
        record_add_field(rec, '980', subfields=[('a', 'OPENAIRE')])
        output = "<collection>%s</collection>" % record_xml_output(rec)

        # Upload MARCXML
        run_sql("TRUNCATE schTASK")  # Ensures we run bibupload
        (hdl, marcxml_path) = mkstemp(suffix=".xml", text=True)
        open(marcxml_path, 'w').write(output)
        task_low_level_submission(
            'bibupload', 'openaire', '-c', marcxml_path, '-P5')
        task_low_level_submission('bibindex', 'openaire')
        task_low_level_submission('webcoll', 'openaire')
        os.system("%s/bin/bibupload 1 > /dev/null" % CFG_PREFIX)
        os.system("%s/bin/bibindex 2 > /dev/null" % CFG_PREFIX)
        os.system("%s/bin/webcoll 3 > /dev/null" % CFG_PREFIX)

    #
    # Assert methods
    #
    def assertPublicationMetadata(self, pub_id, expected_metadata):
        """
        Assert that field values of a publication is equal to those
        given in the expected_metadata dictionary.
        """
        pub = OpenAIREPublication(self.user_id, publicationid=pub_id)
        metadata = pub.metadata

        for field, expected_val in expected_metadata.items():
            if field == 'projects':
                continue
            real_val = metadata.get(field, None)
            if field == 'related_publications':
                # Remove "doi:" and filter out blank strings.
                real_val = real_val.split("\n")

                def _map_func(x):
                    if x.startswith("doi:"):
                        return x[4:]
                    else:
                        return x
                expected_val = filter(
                    lambda x: x, map(_map_func, expected_val.split("\n")))
            self.assertEqual(real_val, expected_val, "Field %s: expected %s but got %s" % (field, expected_val, real_val))

    # ================================
    # Tests
    # ================================
    def setUp(self):
        """
        Create test client, login with the given user and create a new publication.
        """
        if self.user_id == None:
            res = run_sql("SELECT id FROM user WHERE nickname='admin'")
            assert(len(res) == 1, "Couldn't find admin user")
            self.user_id = int(res[0][0])
            
        uname = get_nickname(self.user_id)
        self.assertEqual(uname, "admin")

        self.client = TestClient(response_wrapper=JSONResponse)
        self.client.login(uname, '')
        self.client_noauth = TestClient(response_wrapper=JSONResponse)
        self.pub = OpenAIREPublication(self.user_id)
        self.pub_id = self.pub.publicationid

    def tearDown(self):
        """
        Remove the publication again.
        """
        self.pub.delete()
        self.pub = None
        self.pub_id = None

    def test_verify_field(self):
        """
        Testing of verify field action

        python -m unittest invenio.openaire_deposit_webinterface_tests.AjaxGatewayTest.test_verify_field
        """
        # Language
        res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field('language', 'eng'))
        self.assertEqual(res.json['errors']['language_%s' % self.pub_id], '')
        res = self.client.post("/deposit/ajaxgateway",
                               data=self.action_verify_field('language', ''))
        self.assertNotEqual(
            res.json['errors']['language_%s' % self.pub_id], '')

        # Publication type
        res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field('publication_type', 'publishedArticle'))
        self.assertEqual(
            res.json['errors']['publication_type_%s' % self.pub_id], '')
        res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field('publication_type', 'dfgsdfgsd'))
        self.assertNotEqual(
            res.json['errors']['publication_type_%s' % self.pub_id], '')

        # Report pages no
        res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field('report_pages_no', '6545'))
        self.assertEqual(
            res.json['errors']['report_pages_no_%s' % self.pub_id], '')
        res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field('report_pages_no', 'dfgsdfgsd'))
        self.assertNotEqual(
            res.json['errors']['report_pages_no_%s' % self.pub_id], '')

        # Keywords
        res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field('keywords', 'multiline\nkeywords'))
        self.assertEqual(res.json['errors']['keywords_%s' % self.pub_id], '')
        self.assertEqual(res.json['warnings']['keywords_%s' % self.pub_id], '')
        res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field('keywords', 'this;should;probably;be;separated'))
        self.assertEqual(res.json['errors']['keywords_%s' % self.pub_id], '')
        self.assertNotEqual(
            res.json['warnings']['keywords_%s' % self.pub_id], '')

        # Accept CC0 license
        res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field('accept_cc0_license', 'yes', extra_data={'publication_type': 'data'}))
        self.assertEqual(
            res.json['errors']['accept_cc0_license_%s' % self.pub_id], '')
        self.assertEqual(
            res.json['warnings']['accept_cc0_license_%s' % self.pub_id], '')
        res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field('accept_cc0_license', '', extra_data={'publication_type': 'data'}))
        self.assertNotEqual(
            res.json['errors']['accept_cc0_license_%s' % self.pub_id], '')
        self.assertEqual(
            res.json['warnings']['accept_cc0_license_%s' % self.pub_id], '')
        res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field('accept_cc0_license', '', extra_data={'publication_type': 'report'}))
        self.assertEqual(
            res.json['errors']['accept_cc0_license_%s' % self.pub_id], '')
        self.assertEqual(
            res.json['warnings']['accept_cc0_license_%s' % self.pub_id], '')

        # Related publications
        res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field('related_publications', '10.1234/1234', extra_data={'publication_type': 'data'}))
        self.assertEqual(
            res.json['errors']['related_publications_%s' % self.pub_id], '')
        self.assertEqual(
            res.json['warnings']['related_publications_%s' % self.pub_id], '')
        res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field('related_publications', '10.1234/1234\n\n12.2323', extra_data={'publication_type': 'data'}))
        self.assertNotEqual(
            res.json['errors']['related_publications_%s' % self.pub_id], '')
        self.assertEqual(
            res.json['warnings']['related_publications_%s' % self.pub_id], '')
        res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field('related_publications', '10.1234/1234\n\n10.1234/12342\n10.1234/12342', extra_data={'publication_type': 'data'}))
        self.assertEqual(
            res.json['errors']['related_publications_%s' % self.pub_id], '')
        self.assertEqual(
            res.json['warnings']['related_publications_%s' % self.pub_id], '')

        # Ensure all checks are executed to test for possible runtime errors. Validate is not needed
        for field in CFG_METADATA_FIELDS_CHECKS:
            res = self.client.post("/deposit/ajaxgateway", data=self.action_verify_field(field, 'test'))

    def test_action_save_published_article(self):
        """
        Testing of save action
        """
        data = {
            'access_rights': 'openAccess',
            'embargo_date': '',
            'authors': '',
            'title': 'some title',
            'abstract': '',
            'language': '',
            'original_title': '',
            'original_abstract': '',
            'publication_type': 'publishedArticle',
            'publication_date': '',
            'journal_title': '',
            'doi': '',
            'volume': '',
            'issue': '',
            'pages': '',
            'keywords': '',
            'notes': '',
        }

        res = self.client.post(
            "/deposit/ajaxgateway", data=self.action_save(data=data))
        self.assertPublicationMetadata(
            self.pub_id, {'publication_type': 'publishedArticle'})

    def _submit(self, type, style, submit=True):
        """
        Make a submission
        """
        resp = self.client.get(
            "/deposit", query_string={'style': style, 'ln': 'en'})
        self.assertEqual(resp.status_code, 200)

        # Check if there's any existing submissions
        self.clear_publications('0', style=style)
        self.clear_publications(self.project_id, style=style)

        # Simple file upload
        resp = self.client.post(
            "/deposit",
            query_string={'style': style, 'ln': 'en', 'projectid': '0'},
            data={'Filedata': (StringIO(self.make_stringio_pdf("Type: %s Style: %s" % (type, style))), '%s_%s_file.pdf' % (type.lower(), style)), 'upload': 'Upload'},
        )
        self.assertEqual(resp.status_code, 200)
        pub_ids = self.get_publications_for_project('0', style=style)
        self.assertEqual(len(pub_ids), 1)
        pub_id = pub_ids[0]

        # Link with project
        resp = self.client.post(
            "/deposit/ajaxgateway",
            data={'projectid': self.project_id,
                  'publicationid': pub_id, 'action': 'linkproject'},
        )
        self.assertEqual(resp.json['errors']['projects_%s' % pub_id], '')

        # Save metadata
        fixture = FIXTURES[type]
        self.save_metadata(self.project_id, pub_id, fixture)

        # Submit publication
        if submit:
            run_sql("TRUNCATE schTASK")  # Ensures we run bibupload
            res = self.client.post("/deposit/ajaxgateway", data=self.action_submit(data=fixture, override_pubid=pub_id, projectid=self.project_id))
            self.assertIn("This is a preview of the submitted publication. If approved, it will be available at ", res.json['appends']['#submitted_publications'])

            # Get record id
            m = re.search("/record/(\d+)\"", res.json[
                          'appends']['#submitted_publications'])
            self.assertIsNotNone(m, "Couldn't find record id.")
            rec_id = m.group(1)

            # Run bibupload to get record
            from invenio.config import CFG_PREFIX
            os.system("%s/bin/bibupload 1" % CFG_PREFIX)

            # Approve record so it's publicly available.
            self.approve_record(rec_id)

            # Check if record is reachable
            res = self.client_noauth.get("/record/%s" % rec_id)
            self.assertEqual(res.status_code, 200)

            res = self.client_noauth.get("/record/%s/files/%s_%s_file.pdf" % (
                rec_id, type.lower(), style.lower()))
            if fixture['access_rights'] in ["embargoedAccess", "closedAccess"]:
                self.assertEqual(res.status_code, 302)  # Restricted access.
            else:
                self.assertEqual(res.status_code, 200)

        # Remove submission again
        self.clear_publications('0', style=style)
        self.clear_publications(self.project_id, style=style)

    def test_submission(self):
        """
        Test a complete submission
        """
        for type in ['publishedArticle', ]:
            for style in ['invenio', 'portal']:
                self._submit(type, style, submit=self.test_full_submit)


#
# Create test suite
#
TEST_SUITE = make_test_suite(SubmissionRegressionTest, AjaxGatewayTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
