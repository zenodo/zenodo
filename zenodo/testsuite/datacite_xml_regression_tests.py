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
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from invenio.testutils import make_test_suite, run_test_suite, InvenioTestCase
from lxml import etree
from StringIO import StringIO


class DataCiteXMLRegressionTest(InvenioTestCase):
    def setUp(self):
        """ Set-up schema """
        self.schema = etree.XMLSchema(
            file='http://schema.datacite.org/meta/kernel-2.2/metadata.xsd'
        )

    #
    # Tests
    #
    def test_validate_xml_against_xsd(self):
        """
        Validate generated DataCite XML for all public records
        """
        from invenio.websearch_model import Collection
        from invenio.bibformat import format_record
        from invenio.bibfield import get_record

        etree.clear_error_log()

        for recid in Collection.query.filter_by(name='zenodo').first().reclist:
            try:
                xml = None
                record = get_record(recid)
                for identifier in record.get('related_identifiers', []):
                    if identifier['scheme'] != identifier['scheme'].lower():
                        raise Exception("Record %s has problem with upper-case scheme %s" % (recid, identifier['scheme']))
                if record.get('doi', None):
                    xml = StringIO(format_record(recid, 'dcite'))
                    xml_doc = etree.parse(xml)
                    self.schema.assertValid(xml_doc)
            except Exception, e:
                print recid
                if xml:
                    print xml.getvalue()
                raise e

TEST_SUITE = make_test_suite(DataCiteXMLRegressionTest)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
