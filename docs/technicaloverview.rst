Technical Overview
==================

Following is a STUB until documentation has been finalized.

Configuration
-------------
Base, module, site, instance

Minting test DOIs via DataCite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    (zenodo)$ inveniomanage config set CFG_DATACITE_USERNAME CERN.ZENODO
    (zenodo)$ inveniomanage config set CFG_DATACITE_PASSWORD <password>


Sign in with GitHub and ORCID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please see ``invenio/modules/oauthclient/contrib/github.py``, and
``invenio/modules/oauthclient/contrib/orcid.py`` for how to register remote
applications.

.. code-block:: console

    (zenodo)$ cdvirtualenv
    (zenodo)$ vim var/invenio.base-instance/invenio.cfg

Add the following configuration variable:

.. code-block:: python

    GITHUB_APP_CREDENTIALS = dict(
        consumer_key="",
        consumer_secret="",
    )
    ORCID_APP_CREDENTIALS = dict(
        consumer_key="",
        consumer_secret="",
    )

Note, that ORCID does not allow localhost to be used in redirect URIs thus
making testing in development mode difficult.


Logging to Sentry
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    (zenodo)$ inveniomanage config set SENTRY_DSN <sentry dsn url>


Customization
-------------

Templates
~~~~~~~~~

Views
~~~~~

Menus
~~~~~

Assets
------
Bower, RequireJS, Less, Building, settings.js

Modules
-------
