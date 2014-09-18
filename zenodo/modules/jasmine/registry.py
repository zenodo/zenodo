# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.


"""Registry for Jasmine spec files."""

import os
import re
from werkzeug.utils import import_string
from flask.ext.registry import RegistryProxy
from invenio.ext.registry import DictModuleAutoDiscoverySubRegistry


class JasmineSpecsAutoDiscoveryRegistry(DictModuleAutoDiscoverySubRegistry):

    """Registry for Jasmine spec files.

    Looks into /testsuite/js/*.spec.js in each module.
    """
    pattern = re.compile(".+\.spec.js")

    def __init__(self, *args, **kwargs):
        self.specs_folder = 'js'
        super(JasmineSpecsAutoDiscoveryRegistry, self).__init__(
            'testsuite', **kwargs
        )

    def keygetter(self, key, original_value, new_value):
        return key

    def _walk_dir(self, pkg, base, root):
        for root, dirs, files in os.walk(root):
            for name in files:
                if JasmineSpecsAutoDiscoveryRegistry.pattern.match(name):
                    specfilename = os.path.join(root, name)
                    specpath = "{0}/{1}".format(
                        pkg,
                        specfilename[len(base)+1:]
                    )
                    self.register(specfilename, key=specpath)
            for name in dirs:
                self._walk_dir(pkg, base, os.path.join(root, name))

    def _discover_module(self, pkg):
        """Load list of files from resource directory."""
        import_str = pkg + '.' + self.module_name

        try:
            module = import_string(import_str, silent=self.silent)
            if module is not None:
                for p in module.__path__:
                    specsfolder = os.path.join(p, self.specs_folder)
                    if os.path.isdir(specsfolder):
                        self._walk_dir(pkg, specsfolder, specsfolder)
        except ImportError as e:  # pylint: disable=C0103
            self._handle_importerror(e, pkg, import_str)
        except SyntaxError as e:
            self._handle_syntaxerror(e, pkg, import_str)


specs = RegistryProxy("jasmine.specs", JasmineSpecsAutoDiscoveryRegistry)
