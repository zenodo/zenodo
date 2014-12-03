Requirements
============
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
   with packages that cannot be upgraded to their latest version of package due
   to either problems in Zenodo/Invenio or problems in the package itself.
 - ``base.requirements.txt``: Base requirements for all installations (includes
   all above requirements files as well).
 - ``test.requirements.txt``: Requirements needed to run the tests (includes
   all above requirements files as well).
 - ``dev.requirements.txt``: Requirements needed for development environments (includes
   all above requirements files as well).

**Zenodo/Invenio branch requirements:**

 - ``requirements.txt``: Default development setup requirements (includes
   ``dev.requirements.txt`` as well as ``master``/``pu-zenodo`` branches of
   Zenodo/Invenio.)
 - ``requirements.master.txt``: Default master requirements (includes
   ``base.requirements.txt`` as well as ``master``/``pu-zenodo`` branches of
   Zenodo/Invenio.)
 - ``requirements.qa.txt``: Default QA requirements (includes
   ``base.requirements.txt`` as well as ``qa`` branches of
   Zenodo/Invenio.)
 - ``requirements.production.txt``: Default production requirements (includes
   ``base.requirements.txt`` as well as ``production`` branches of
   Zenodo/Invenio.)

Above organization of requirements ensures among other issues that dev/test
requirements are not installed on production systems, and that our CI system
can test pull requests against the correct Invenio branch.

Updating requirements
---------------------
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