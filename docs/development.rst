.. _development_process:

Development process
===================

Coding standards
----------------
Zenodo closely follows Invenio's coding standards, which is primarily based on existing standards:

 * PEP8 (Python source code style, including import sorting).
 * PEP257 (Python documentation).
 * PyFlakes (for liniting)

Don't hesitate to ask us if you have any questions.

Editors
~~~~~~~
It is essential for Zenodo developers to install source code linting in their editor in order to be efficient and avoid annoyance over failing automated checks. Below we list packages that our developers are using:

- SublimeText: Package Control, Anaconda, EditorConfig, Git, isort, SideBarEnhancements.
- ...

Additionally Zenodo comes with an ``.editorconfig`` to configure the basics of your favorite editor using `EditorConfig <http://editorconfig.org>`_.

Commit messages
~~~~~~~~~~~~~~~
Please have a look at the commit log history for examples of how to write commit messages.

Contributor agreement
---------------------
By making a pull request against our repository, we assume that you agree to
license your contribution under GPLv2 (source code) / Creative Commons
Attribution 4.0 International (text content).

If you are a new contributor please ensure to add yourself to the ``AUTHORS``
file.

Source code file header
~~~~~~~~~~~~~~~~~~~~~~~
The standard source code file header should be included in all files (here
a Python example):

.. code-block:: python

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

.. _branches:

Branches
--------
Zenodo has three active branches:

* ``master`` - Default development branch (https://github.com/zenodo/zenodo/tree/master).
* ``qa`` - Quality assurance branch (https://github.com/zenodo/zenodo/tree/qa).
* ``production`` - Production branch (https://github.com/zenodo/zenodo/tree/production).

Tags
~~~~
Zenodo only uses tags to mark major changes in the code base. In particular releases are not tagged since they are managed through branches. Currently the following tags exists:

* ``legacy-20140305`` -- Zenodo prior to being rebased to Invenio's new module
  system (5 March 2014).
* ``legacy-20130508`` -- The OpenAIRE Orphan Record Repository prior to getting
  a make-over and being transformed into Zenodo (8 March 2013, which is also
  the Zenodo launch date).


Testing
-------
Contributions must provide test cases in order to ensure the features can be
tested automatically in our continues integration system. Please also ensure
you check your test coverage to see what you are missing to test.

Running tests
~~~~~~~~~~~~~

You can run all tests (PEP257, import sorting, MANIFEST check, Sphinx
documentation, doctests and Python tests) using the provided script:

.. code-block:: console

    (zenodo)$ ./run-tests.sh

Running Python tests
~~~~~~~~~~~~~~~~~~~~
Python tests will automatically create and destroy a test database so all you
need is:

.. code-block:: console

   (zenodo)$ python setup.py test

You can run individual tests using py.test:

.. code-block:: console

   (zenodo)$ cdvirtualenv src/zenodo
   (zenodo)$ py.test tests/tests_zenodo.py::test_version

Writing Python tests
~~~~~~~~~~~~~~~~~~~~
Please explore existing test cases for examples of how to test Flask-based
applications. Test coverage is automatically displayed for Python tests.

Python requirements
-------------------
Zenodo package requirements are defined in two places:

- ``setup.py``: Defines abstract requirements on packages (i.e. dependency on
  a package but not its specific version, nor its subpackages).
- ``requirements.txt``: Defines concrete requirements on packages (i.e specific
  version of a package, and all dependent subpackages).

This separation between abstract and concrete requirements ensures that the
Zenodo can be run and tested on multiple versions of dependent packages, while
for production deployments we can control the exact version of all dependent
packages.

.. note::
   For more information on abstract vs concrete requirements see
   https://caremad.io/2013/07/setup-vs-requirement/

The concrete requirements for Zenodo are divided over a number of
requirements files which broadly falls in two categories:

**Base requirements:**

 - ``requirements.pinned.txt``: Base requirements for all installations
   with packages that cannot be upgraded to their latest version due
   to either problems in Zenodo or problems in the related packages.
 - ``requirements.txt``: Base requirements for all installations (includes all above requirements files as well).
 - ``requirements.devel.txt``: Requirements for development versions of dependent packages.

**Zenodo developer requirements:**

 - ``requirements.developer.txt``: Requirements for quickly installing all of
   Zenodo requirements as well as development dependencies for e.g. running
   tests.

.. _updateing_requirements:

Updating Python requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
At the beginning of every sprint cycle the Python requirements should be
updated to ensure that Zenodo is always running against the latest versions of
packages with fixes and security patches. The review should always be done in
the beginning of the sprint cycle, to ensure that issues with updated packages
can be discovered as early as possible.

Following is a short recipe for how to update the requirements. First create
a clean virtual environment and install the current requirements.

.. code-block:: console

    $ mkvirtualenv zenodo-req
    (zenodo-req)$ cdvirtualenv
    # Install current requirements
    (zenodo-req)$ pip install -r <path to>/src/zenodo/requirements.txt
    (zenodo-req)$ pip freeze > req-current.txt

Next we use ``pip-tools`` to review and install all updated requirements.
Please be aware that requirements in
``src/zenodo/requirements.pinned.txt`` should not be updated without also
fixing the issues in Zenodo or the related package.

.. code-block:: console

    (zenodo-req)$ pip install pip-tools
    (zenodo-req)$ pip-review --interactive
    (zenodo-req)$ pip freeze > req-new.txt
    # Diff current vs new requirements
    (zenodo-req)$ diff req-current.txt req-new.txt

Now manually update ``src/zenodo/requirements.txt`` with changes displayed
in the diff.

If an upgraded package causes issues, and the problem cannot easily be fixed,
it should be moved from ``requirements.txt`` into
``requirements.pinned.txt`` so it is clear which packages can easily be
updated and which cannot.
