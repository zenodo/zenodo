.. _development_guide:

Development guide
===================

This guide is intended for Zenodo developers, in it you will learn how to
contribute the code to Zenodo.

Developing code locally
~~~~~~~~~~~~~~~~~~~~~~~

To make a code contribution to Zenodo you will either have to submit a patch
to Zenodo repository, but most likely also to one or more of the corresponding
Invenio modules. This is because most of Zenodo's code is referring to Invenio
modules, with only a thin customization and configuration layer on top.
Making changes to Zenodo's code on your local
instance are straightforward - just edit the code and restart the Zenodo
application (sometimes also the Celery worker if you've edit any of the
asynchronous tasks code).

To make local changes to an Invenio module you will need to check out the
code locally. The best way is to check out the
corresponding repository into ~/src/ directory and then install it into your
virtual environment from there.

For example to edit the Invenio-Communities module, check out the
Invenio-Communities code to a local repository:

.. code-block:: console

   $ cd ~/src/
   $ git clone https://github.com/inveniosoftware/invenio-communities.git

Uninstall the installed PyPI version of the module and install the local one:

.. code-block:: console

   $ workon zenodo
   (zenodo) $ pip uninstall invenio-communities
   (zenodo) $ cd ~/src/invenio-communities
   (zenodo) $ pip install -e ".[all]"

.. note::

    The ``-e`` flag in the ``pip install`` is important for the development.
    This way the module will be installed in "editable" mode, meaning that
    you will be able edit the code in directly in
    ``~/src/invenio-communities``, and have the changes be immediately
    available in the installed library inside the virtual environment.

If you now restart the Zenodo application, the relevant ``invenio_communities``
module code should be executed from the locally stored repository in
``~/src/invenio-communities/``.
If you now change the code in ~/src/invenio-communities/ the changes
should be propagated to the Zenodo application.

.. note::

    Please know that if you check out the master version of any Invenio
    module, it's usually much newer version than the release (PyPI) version.
    This means that if the Zenodo-specified version of the module (see `setup.py <https://github.com/zenodo/zenodo/blob/master/setup.py>`_)
    is far behind the master branch, you can expect some incompatibilities
    or strange behaviour.

Making a contribution
~~~~~~~~~~~~~~~~~~~~~

If the feature you've implemented involves only the changes in Zenodo
repository, you will only need to create one PR to Zenodo. If the changes
involve also any of the Invenio modules, you will also have to create a PR in
that corresponding Invenio repository on GitHub.

The recommended way to create a PR is to first fork the repository on GitHub
(both Zenodo and Invenio repositories), push the changes to your fork's
feature branch and create a PR on GitHub against
``[upstream-repository]:[master]`` and ``[your-fork]:[feature-branch]``

In the Zenodo PR, please refer to any relevant Invenio PR on which it depends
so the Zenodo reviewers can also review the Invenio PR changes.
