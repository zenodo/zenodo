
# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
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

"""Mock HTTPretty.

HTTPretty fix related to SSL bug:
https://github.com/gabrielfalcao/HTTPretty/issues/242
"""


import httpretty
import httpretty.core
from httpretty import HTTPretty as OriginalHTTPretty

try:
    from requests.packages.urllib3.contrib.pyopenssl import \
        inject_into_urllib3, extract_from_urllib3
    pyopenssl_override = True
except:
    pyopenssl_override = False


class MyHTTPretty(OriginalHTTPretty):
    """
    HTTPretty mock.

    pyopenssl monkey-patches the default ssl_wrap_socket() function in the
    'requests' library, but this can stop the HTTPretty socket monkey-patching
    from working for HTTPS requests.

    Our version extends the base HTTPretty enable() and disable()
    implementations to undo and redo the pyopenssl monkey-patching,
    respectively.
    """

    @classmethod
    def enable(cls):
        """Enable method mock."""
        OriginalHTTPretty.enable()
        if pyopenssl_override:
            # Take out the pyopenssl version - use the default implementation
            extract_from_urllib3()

    @classmethod
    def disable(cls):
        """Disable method mock."""
        OriginalHTTPretty.disable()
        if pyopenssl_override:
            # Put the pyopenssl version back in place
            inject_into_urllib3()


# Substitute in our version
HTTPretty = MyHTTPretty

httpretty.core.httpretty = MyHTTPretty

# May need to set other module-level attributes here, e.g. enable, reset etc,
# depending on your needs
httpretty.httpretty = MyHTTPretty
