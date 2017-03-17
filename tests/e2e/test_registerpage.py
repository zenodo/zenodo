# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""E2E integration tests."""

from __future__ import absolute_import, print_function

from flask import url_for
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support\
        import expected_conditions as EC
from signal import signal, SIGPIPE, SIG_DFL
import time
# Ignore SIG_PIPE and don't throw exceptions on it...
# (http://docs.python.org/library/signal.html)
signal(SIGPIPE, SIG_DFL)


def test_registerpage(live_server, env_browser):
    """Test retrieval of registerpage."""
    env_browser.get(
        url_for('security.register', _external=True))
    email = 'info@zenodo.org'
    username = 'info'
    password = 'tester'
    elem = env_browser.find_element_by_id("email")
    elem.send_keys(email)
    elem = env_browser.find_element_by_id("profile.username")
    elem.send_keys(username)
    elem = env_browser.find_element_by_id("password")
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)
    # env_browser.find_element_by_tag_name("form").submit()
    success = "Thank you. Confirmation instructions have been sent to"
    already = "is already associated with an account."
    time.sleep(5)
    elem = env_browser.find_element_by_tag_name("body").text
    if already in elem:
        assert already in elem
    else:
        assert success in elem
