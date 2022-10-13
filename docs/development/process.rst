.. _development_process:

Development process
===================

Coding standards
----------------
Zenodo closely follows Invenio's coding standards, which is primarily based on existing standards:

 * `PEP8 <https://www.python.org/dev/peps/pep-0008>`_ (Python source code style, including import sorting).
 * `PEP257 <https://www.python.org/dev/peps/pep-0257>`_ (Python documentation).
 * `PyFlakes <https://pypi.python.org/pypi/pyflakes>`_ (for liniting)

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
requirements files which broadly fall in two categories:

**Base requirements:**

 - ``requirements.pinned.txt``: Base requirements for all installations
   with packages that cannot be upgraded to their latest version due
   to either problems in Zenodo or problems in the related packages.
 - ``requirements.txt``: Base requirements for all installations (includes all above requirements files as well).

.. _updating_requirements:

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

    $ mkvirtualenv zenodo-current
    (zenodo-current)$ cdvirtualenv
    # Install current requirements
    (zenodo-current)$ pip install -r <path to>/src/zenodo/requirements.txt
    (zenodo-current)$ pip freeze > reqs-current.txt
    # Delete the virtualenv
    (zenodo-current)$ deactivate
    $ rmvirtualenv zenodo-current

The quickest way to update the packages is to create a new virtualenv and to
install the latest package versions. Please be aware that requirements in
``src/zenodo/requirements.pinned.txt`` should not be updated without also
fixing the issues in Zenodo or the related package.

.. code-block:: console

    $ mkvirtualenv zenodo-update
    # Install from setup.py, to get latest versions of dependencies
    (zenodo-update)$ pip install -e .[postgres,elasticsearch2]
    (zenodo-update)$ pip freeze > reqs-update.txt
    # Diff current vs new requirements
    (zenodo-update)$ diff reqs-current.txt reqs-update.txt

Now manually review the diff and update ``src/zenodo/requirements.txt``. Things
to keep in mind:

- If a dependency has a major or minor version bump (i.e. ``1.3.0 -> 2.0.0`` or
  ``1.3.0`` -> ``1.5.0``), check the package's changelog for breaking changes,
  deprecations and fixes.
- If a dependency introduces a breaking change/feature that cannot easily be
  fixed on our side, try to update only the minor/patch version and pin
  appropriately in setup.py (e.g. if Flask ``1.1.x`` breaks something, put
  ``'Flask>=1.0.0,<1.1.0'`` in ``install_requires``).

If you want to have a closer look at the changes and dependency relationships,
use ``pip-tools`` to review and install all updated requirements.

.. code-block:: console

    (zenodo-update)$ pip install pip-tools
    (zenodo-update)$ pip-compile

Expanding Zenodo metadata checklist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here you will find a short checklist/guide on how to add a new field to the
metadata model, and what are the related files and models (ES mappings, UI
deposit form), that need to be taken into consideration when such a change is
made.

1. Update the Record and Deposit JSONSchemas and ES mappings
    a) To update any JSONSchema, you have to modify `records/jsonschemas/records/base-v1.0.0 <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/records/jsonschemas/records/base-v1.0.0.json>`_ and then compile the rest of the JSONSchemas via the ``zenodo jsonschemas ...`` commands. **DO NOT** modify the following JSONSchemas by hand (unless you know what you're doing), as they need to be compiled from their sources (if you mess up there are tests in place that will catch any inconsistencies though)
        - **Deposit**: Compile `deposit/jsonschemas/deposits/records/record-v1.0.0.json <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/deposit/jsonschemas/deposits/records/record-v1.0.0.json>`_ by running ``zenodo jsonschemas compiledeposit -d``
        - **Record**: Compile `records/jsonschemas/records/record-v1.0.0.json <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/records/jsonschemas/records/record-v1.0.0.json>`_ by running ``zenodo jsonschemas compilerecord -d``
    b) Update ES mappings by editing them directly
        - **Record**: `records/mappings/records/record-v1.0.0.json <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/records/mappings/records/record-v1.0.0.json>`_
        - **Deposit**: `deposit/mappings/deposits/records/record-v1.0.0.json <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/deposit/mappings/deposits/records/record-v1.0.0.json>`_
2. Update Deposit and Record REST API (JSON serialisers/deserialisers)
    - **Common**: `records/serializers/schemas/common.py <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/records/serializers/schemas/common.py>`_
    - **Deposit/Legacy**: `records/serializers/schemas/legacyjson.py <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/records/serializers/schemas/legacyjson.py>`_
    - **New**: `records/serializers/schemas/json.py <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/records/serializers/schemas/json.py>`_
3. Add to UI form (need to decide exactly where on how it should be displayed)
    - **Deposit Form JSONSchema**: `deposit/static/json/zenodo_deposit/deposit_form.json <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/deposit/static/json/zenodo_deposit/deposit_form.json>`_
    - Check if there are any **Angular templates/directives** `deposit/static/templates/zenodo_deposit <https://github.com/zenodo/zenodo/tree/master/zenodo/modules/deposit/static/templates/zenodo_deposit>`_ modifications required to implement the functionality of the new fields on the deposit form page
4. Serialization format updates
    - **DataCite**: `records/serializers/schemas/datacite.py <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/records/serializers/schemas/datacite.py>`_
        - `DataCite Metadata Schema v3.1 <https://schema.datacite.org/meta/kernel-3.1/>`_
        - `DataCite Metadata Schema v4.1 <https://schema.datacite.org/meta/kernel-4.1/>`_
    - **DublinCore**: `records/serializers/schemas/dc.py <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/records/serializers/schemas/dc.py>`_
        - `DCMI Metadata Terms <http://dublincore.org/documents/dcmi-terms/>`_
    - **OpenAIRE JSON**: `openaire/schema.py <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/openaire/schema.py>`_
        - `OpenAIRE Schema <https://www.openaire.eu/schema/1.0/oaf-result-1.0.xsd>`_
    - **CSL**: `records/serializers/schemas/csl.py <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/records/serializers/schemas/csl.py>`_
        - `CSL Terms <http://docs.citationstyles.org/en/stable/specification.html#appendix-ii-terms>`_
    - **BibTex**: `records/serializers/bibtex.py <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/records/serializers/bibtex.py>`_
        - `BibTeX documentation <http://ctan.math.washington.edu/tex-archive/biblio/bibtex/base/btxdoc.pdf>`_
    - **MARC21**: `records/serializers/schemas/marc21.py <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/records/serializers/schemas/marc21.py>`_
    - **JSON-LD (schema.org)**: `records/serializers/schemas/schemaorg.py <https://github.com/zenodo/zenodo/blob/master/zenodo/modules/records/serializers/schemas/schemaorg.py>`_
5. Update `deposit REST API documentation <https://github.com/zenodo/developers.zenodo.org/blob/master/source/includes/resources/deposit/_representation.md>`_

Adding Resource Types
^^^^^^^^^^^^^^^^^^^^^

Resource types follow a two-level hierarchy of ``<type> -> <sub-type>`` (e.g.
"Image" -> "Figure"). Especially when adding (or updating) resource types (e.g.
a new "Publication" sub-type), besides checking the above places, you have to
also update the `records/data/objecttypes.json
<https://github.com/zenodo/zenodo/blob/master/zenodo/modules/records/data/objecttypes.json>`_
file accordingly with a new entry:

- **internal_id**: Unique internal ID for the type. Basically ``<type>`` (e.g. ``software``) or ``<type>-<sub-type>`` (e.g. ``image-figure``).
- **id**: JSONSchema ID field. Basically ``https://zenodo.org/objecttypes/<type>`` or ``https://zenodo.org/objecttypes/<type>/<sub-type>``. Example ``https://zenodo.org/objecttypes/publication/softwaredocumentation#``
- **parent**: If a ``sub-type``, this points to the ``type``'s ``id``. Example: ``{"$ref": "https://zenodo.org/objecttypes/publication"}``
- **title**: Title for the type. Example: ``{"en": "Software documentation"}``
- **title_plural**: Title in plural. Example: ``{"en": "Software documentation"}``
- **schema.org**: Schema.org DataType, should be CreativeWork or one of its appropriate subtypes (`vocabulary <https://schema.org/CreativeWork#subtypes>`__). Example: ``https://schema.org/CreativeWork``
- **datacite**: DataCite ResourceType (`vocabulary <https://schema.datacite.org/meta/kernel-4.4/doc/DataCite-MetadataKernel_v4.4.pdf>`__). Example: ``{"general": "Text", "type": "Software documentation"}``
- **eurepo**: ``info-eu-repo`` type (`vocabulary <https://wiki.surfnet.nl/display/standards/info-eu-repo>`__). Example: ``info:eu-repo/semantics/technicalDocumentation``
- **openaire**: OpenAIRE-specific fields
    - **resourceType**: OpenAIRE resource type code (`vocabulary <https://beta.openaire.eu/research-products-and-their-associated-types-in-openaire>`__). Example: ``0009``
    - **type**: OpenAIRE type used for direct indexing. Can be ``publication``, ``dataset``, ``software`` or ``other``
- **csl**: Citation Style Language type (`vocabulary <http://docs.citationstyles.org/en/stable/specification.html#appendix-iii-types>`__). Example: ``article``
