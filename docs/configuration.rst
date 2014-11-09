Configuration
=============

4.1. Minting test DOIs via DataCite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    (zenodo)$ inveniomanage config set CFG_DATACITE_USERNAME CERN.ZENODO
    (zenodo)$ inveniomanage config set CFG_DATACITE_PASSWORD <password>


4.2. Sign in with GitHub and ORCID
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


4.3. Logging to Sentry
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    (zenodo)$ inveniomanage config set SENTRY_DSN <sentry dsn url>