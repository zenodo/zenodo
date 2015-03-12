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

Kwalitee
~~~~~~~~
All Zenodo commits are tested using the Invenio Kwalitee tool which performs pyflakes, PEP8, PEP257, Copyright and license header checks as well as commit message checks. Developers should install this tool locally when developing in order to prevent making pull requests that will fail checks:

.. code-block:: console

    (zenodo)$ pip installl kwalitee
    (zenodo)$ cd $HOME/src/invenio/
    (zenodo)$ kwalitee githooks install
    (zenodo)$ cd $HOME/src/zenodo/
    (zenodo)$ kwalitee githooks install

Kwalitee checks can be circumvented by using:

.. code-block:: console

    (zenodo)$ git commit --no-verify

See https://github.com/jirikuncar/kwalitee for further details.

Contributor agreement
---------------------
By making a pull request against our repository, we assume that you agree to
license your contribution under GPLv3 (source code) / Creative Commons
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
    # Copyright (C) <YEAR> CERN.
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

.. _branches:

Branches
--------
Zenodo has three active branches:

* ``master`` - Default development branch (https://github.com/zenodo/zenodo/tree/master).
* ``qa`` - Quality assurance branch (https://github.com/zenodo/zenodo/tree/qa).
* ``production`` - Production branch (https://github.com/zenodo/zenodo/tree/production).

Zenodo depends on specific versions of Invenio, which are managed using
an Invenio fork located at https://github.com/zenodo/invenio. The Invenio fork has
three branches:

* ``zenodo-master`` -- Default development branch that works with Zenodo ``master`` branch (https://github.com/zenodo/invenio/tree/zenodo-master).
* ``qa`` -- Quality assurance branch that works with Zenodo ``qa`` branch (https://github.com/zenodo/invenio/tree/qa).
* ``production`` -- Production branch that works with Zenodo ``production`` branch (https://github.com/zenodo/invenio/tree/production).

The main purpose of the Invenio fork is to 1) manage which specific version of Invenio that Zenodo works with, and 2) allow for applying hot and quick fixes prior to their integration in upstream Invenio. Deviations from upstream must be kept at a bare minimum to make rebasing to latest upstream Invenio as easy as possible and prevent the fork from diverging.

.. note::
    Our Invenio fork is regularly rebased to the latest Invenio development version, thus be careful when fetching updates to not overwrite your own changes.

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
Contributions must provide test cases in order to ensure the features can be tested
automatically in our continues integration system. Please also ensure you check your
test coverage to see what you are missing to test.

Running Python tests
~~~~~~~~~~~~~~~~~~~~

Python test requires you have a clean database:

.. code-block:: console

   (zenodo)$ inveniomanage database init --yes-i-know
   (zenodo)$ inveniomanage database create
   (zenodo)$ python setup.py test

You can run individual tests by simply executing the test file, e.g.:

.. code-block:: console

   (zenodo)$ cdvirtualenv src/zenodo
   (zenodo)$ nosetests zenodo/base/testsuite/test_jsonext.py:TestReaders.test_marc_export

Writing Python tests
~~~~~~~~~~~~~~~~~~~~
Please explore existing test cases for examples of how to test Flask-based applications. In particular
we provide many wrappers that allow easy testing of HTTP interactions.

Running JavaScript tests
~~~~~~~~~~~~~~~~~~~~~~~~

Please see http://invenio.readthedocs.org/en/latest/ext/jasmine.html

Test coverage
~~~~~~~~~~~~~
You can check your Python test coverage like this:

.. code-block:: console

   (zenodo)$ pip install coverage
   (zenodo)$ inveniomanage database create
   (zenodo)$ nosetests --with-coverage --cover-package=zenodo.modules.mymodule test_myfile.py


Selenium
~~~~~~~~
Selenium tests will be introduced in the near future.


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

 - ``base-pinned.requirements.txt``: Base requirements for all installations
   with packages that cannot be upgraded to their latest version due
   to either problems in Zenodo/Invenio or problems in the package itself.
 - ``base.requirements.txt``: Base requirements for all installations (includes
   all above requirements files as well).
 - ``test.requirements.txt``: Requirements needed to run the tests (includes
   all above requirements files as well).
 - ``dev.requirements.txt``: Requirements needed for development environments (includes
   all above requirements files as well).

**Zenodo/Invenio branch requirements:**

 - ``requirements.txt``: Default development setup requirements (includes
   ``dev.requirements.txt`` as well as ``master``/``zenodo-master`` branches of
   Zenodo/Invenio.)
 - ``requirements.master.txt``: Default master requirements (includes
   ``base.requirements.txt`` as well as ``master``/``zenodo-master`` branches
   of Zenodo/Invenio.)
 - ``requirements.qa.txt``: Default QA requirements (includes
   ``base.requirements.txt`` as well as ``qa`` branches of
   Zenodo/Invenio.)
 - ``requirements.production.txt``: Default production requirements (includes
   ``base.requirements.txt`` as well as ``production`` branches of
   Zenodo/Invenio.)

Above organization of requirements ensures among other issues that dev/test
requirements are not installed on production systems, and that our CI system
can test pull requests against the correct Invenio branch.

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
    (zenodo-req)$ pip install -r <path to>/src/zenodo/requirements.master.txt
    (zenodo-req)$ pip freeze > req-current.txt

Next we use ``pip-tools`` to review and install all updated requirements.
Please be aware that requirements in
``src/zenodo/base-pinned.requirements.txt`` should not be updated without also
fixing the issues in Invenio/Zenodo.

.. code-block:: console

    (zenodo-req)$ pip install pip-tools
    (zenodo-req)$ pip-review --interactive
    (zenodo-req)$ pip freeze > req-new.txt
    # Diff current vs new requirements
    (zenodo-req)$ diff req-current.txt req-new.txt

Now manually update ``src/zenodo/base.requirements.txt`` with changes displayed
in the diff.

If an upgraded package causes issues, and the problem cannot easily be fixed,
it should be moved from ``base.requirements.txt`` into
``base-pinned.requirements.txt`` so it is clear which packages can easily be
updated and which cannot.

.. _invenio_rebasing:

Invenio upgrade process
-----------------------
Zenodo depends on specific development version of Invenio, which is managed
using an Invenio fork located at https://github.com/zenodo/invenio. A controlled
Invenio upgrade process is critical to ensure Zenodo service stability as well
as ensuring that Zenodo can benefit from the latest developments in Invenio.

As with the Python requirements, the Invenio fork is rebased at the beginning of
each sprint cycle in order to be able to test and fix stability issues during the
sprint cycle. In addition to the controlled Invenio upgrade process it is essential
for Zenodo developers to monitor and engage in Invenio development, to ensure
that potential issues are detected early.

.. note::

    This is normally done by an integrator, and not by every developer.

First update your local *master* branch with upstream changes:

.. code-block:: console

    (zenodo)$ cdvirtualenv src/invenio
    (zenodo)$ git fetch upstream
    (zenodo)$ git checkout master
    (zenodo)$ git merge --ff-only upstream/master
    (zenodo)$ git checkout zenodo-master

Review which of the commits in ``zenodo-master`` that have already been
integrated in Invenio:

.. code-block:: console

    (zenodo)$ git log --oneline master..zenodo-master

Note, commits from ``zenodo-master`` that was integrated in Invenio, will not
automatically be filtered out since they usually have a different SHA.

Review changes in ``master``:

.. code-block:: console

    (zenodo)$ git log --oneline zenodo-master..master
    (zenodo)$ git log -u zenodo-master..master

Checklist:
 - Commit log (search for ``NOTE`` bullet points in commit messages).
 - Requirements changes (i.e. changes to ``invenio/setup.py`` or
   ``invenio/requirements.txt``) must usually be updated in Zenodo's
   ``zenodo/base.requirements.txt``.
 - Bower shim changes (i.e. ``invenio/base/static/js/settings.js``) must be
   updated in ``zenodo/base/static/js/settings.js``.
 - New and/or changed database models (i.e. ``models.py`` + upgrade scripts)
   needs to properly tested prior to production deployment.
 - New Invenio modules which might need to be included in
   ``zenodo/config.py:PACKAGES``.
 - New configuration variables (``config.py`` and ``invenio.conf``).

Rebase the Invenio fork's ``zenodo-master`` branch (it is advisable to create a
working branch and rebase that branch, since you may need several rebase
iterations in case of conflicting changes):

.. code-block:: console

    (zenodo)$ git checkout -b aaa zenodo-master
    (zenodo)$ git rebase -i master
    (zenodo)$ git branch -m zenodo-master zenodo-master-old
    (zenodo)$ git branch -m aaa zenodo-master

Once rebased, make a pull request against Invenio with the commits in
``zenodo-master`` that are ready for integration:

.. code-block:: console

    (zenodo)$ git log --oneline master..zenodo-master
