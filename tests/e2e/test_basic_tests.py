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

from signal import SIG_DFL, SIGPIPE, signal
from time import sleep

import flask
from invenio_accounts import testutils
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from six.moves.urllib.request import urlopen

# Ignore SIG_PIPE and don't throw exceptions on it...
# (http://docs.python.org/library/signal.html)
signal(SIGPIPE, SIG_DFL)


def test_registerpage(live_server, env_browser):
    # """Test retrieval of registerpage."""
    # env_browser.get(
    #     url_for('security.register', _external=True))
    # email = 'info@zenodo.org'
    # username = 'info'
    # password = 'tester'
    # elem = env_browser.find_element_by_id("email")
    # elem.send_keys(email)
    # elem = env_browser.find_element_by_id("profile.username")
    # elem.send_keys(username)
    # elem = env_browser.find_element_by_id("password")
    # elem.send_keys(password)
    # elem.send_keys(Keys.RETURN)
    # env_browser.find_element_by_name("register_user_form").submit()
    # success = "Thank you. Confirmation instructions have been sent to"
    # already = "is already associated with an account."
    # time.sleep(5)
    # elem = env_browser.find_element_by_tag_name("body").text
    # if already in elem:
    #     assert already in elem
    # else:
    #     assert success in elem

    """E2E user registration and login test."""
    browser = env_browser
    # 1. Go to user registration page
    browser.get(flask.url_for('security.register', _external=True))
    assert (flask.url_for('security.register', _external=True) in
            browser.current_url)
    # 2. Input user data
    signup_form = browser.find_element_by_name('register_user_form')
    input_email = signup_form.find_element_by_name('email')
    input_password = signup_form.find_element_by_name('password')
    input_username = env_browser.find_element_by_id("profile.username")
    # input w/ name "email"
    # input w/ name "username"
    # input w/ name "password"
    user_email = 'test@example.org'
    user_password = '12345_SIx'
    user_name = 'test'
    input_email.send_keys(user_email)
    input_password.send_keys(user_password)
    input_username.send_keys(user_name)

    # 3. submit form
    signup_form.submit()
    sleep(1)  # we need to wait after each form submission for redirect

    # ...and get redirected to the "home page" ('/')
    # This isn't a very important part of the process, and the '/' url isn't
    # even registered for the Invenio-Accounts e2e app. So we don't check it.

    # 3.5: After registering we should be logged in.
    browser.get(flask.url_for('security.change_password', _external=True))
    assert (flask.url_for('security.change_password', _external=True) in
            browser.current_url)

    # 3.5: logout.
    browser.get(flask.url_for('security.logout', _external=True))
    assert not testutils.webdriver_authenticated(browser)

    # 4. go to login-form
    browser.get(flask.url_for('security.login', _external=True))
    assert (flask.url_for('security.login', _external=True) in
            browser.current_url)
    login_form = browser.find_element_by_name('login_user_form')
    # 5. input registered info
    login_form.find_element_by_name('email').send_keys(user_email)
    login_form.find_element_by_name('password').send_keys(user_password)
    # 6. Submit!
    # check if authenticated at `flask.url_for('security.change_password')`
    login_form.submit()
    sleep(1)

    assert testutils.webdriver_authenticated(browser)

    browser.get(flask.url_for('security.change_password', _external=True))
    assert (flask.url_for('security.change_password', _external=True) in
            browser.current_url)
