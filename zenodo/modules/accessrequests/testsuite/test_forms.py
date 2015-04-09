# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Model tests."""

from __future__ import absolute_import

from datetime import date, timedelta

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite


class AccessRequestFormTestCase(InvenioTestCase):

    """Test access request form."""

    def test_validation(self):
        """Test validation."""
        from ..forms import AccessRequestForm

        assert not AccessRequestForm(
            full_name="  ", email="   ", justification="  ").validate()
        assert not AccessRequestForm(
            full_name="Test", email="", justification="").validate()
        assert not AccessRequestForm(
            full_name="Test", email="info", justification="").validate()
        assert not AccessRequestForm(
            full_name="Test", email="info", justification="info").validate()
        assert AccessRequestForm(
            full_name="Test", email="info@invenio-software.org",
            justification="info").validate()


class ApprovalFormTestCase(InvenioTestCase):

    """Test approval form."""

    def test_validation(self):
        """Test validation."""
        from ..forms import ApprovalForm

        today = date.today()
        yesterday = date.today()+timedelta(days=-1)
        tomorrow = date.today()+timedelta(days=1)
        oneyear = date.today()+timedelta(days=365)
        oneyearoneday = date.today()+timedelta(days=366)

        assert not ApprovalForm(
            message="", expires_at="", accept=True).validate()
        assert not ApprovalForm(
            message="", expires_at="", reject=True).validate()
        assert not ApprovalForm(
            message="test", expires_at=tomorrow, accept=True, reject=True
        ).validate()

        # Accept + date validation
        assert ApprovalForm(
            message="", expires_at=tomorrow, accept=True).validate()
        assert ApprovalForm(
            message="", expires_at=oneyear, accept=True).validate()
        assert not ApprovalForm(
            message="", expires_at=today, accept=True).validate()
        assert not ApprovalForm(
            message="", expires_at=yesterday, accept=True).validate()
        assert not ApprovalForm(
            message="", expires_at=oneyearoneday, accept=True).validate()

        # Reject + message
        assert ApprovalForm(
            message="a message", expires_at="", reject=True).validate()
        assert not ApprovalForm(
            message="", expires_at="", reject=True).validate()
        assert not ApprovalForm(
            message="      ", expires_at="", reject=True).validate()


TEST_SUITE = make_test_suite(ApprovalFormTestCase, AccessRequestFormTestCase)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
