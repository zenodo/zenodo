# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
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

r"""Zenodo usage documentation for developers.

.. _running:

Running
-------
Starting a development server is as simple as (note, if you are using docker,
simply run ``docker-compose up``):

.. code-block:: console

   $ zenodo --debug run

Celery workers can be started using the command:

.. code-block:: console

   $ celery worker -A zenodo.celery -l INFO

Configuration
-------------
Out-of-the-box Zenodo is configured to run in a local development environment
with all services running on localhost. Some Zenodo features are dependent
on external services, which by default are not configured - e.g. ORCID/GitHub
sign-in. In order to make these features work, please follow the guide below
for how to configure them.

Instance configuration
~~~~~~~~~~~~~~~~~~~~~~
You can configure your specific instance by either environment variables
and/or using the instance configuration file located at:

.. code-block:: console

    ${VIRTUAL_ENV}/var/instance/zenodo.cfg

Recaptcha
~~~~~~~~~
To enable Recaptcha on the sign up page, you need to get a public and private
key from https://www.google.com/recaptcha/ and add them to your configuration:

.. code-block:: python

   RECAPTCHA_PUBLIC_KEY = '...'
   RECAPTCHA_PRIVATE_KEY = '...'

ORCID Login
~~~~~~~~~~~
In order to enable ORCID login you must get an OAuth client id and client
secret from ORCID and add them to:

.. code-block:: python

   ORCID_APP_CREDENTIALS = dict(
       consumer_key='...',
       consumer_secret='...',
   )

GitHub Login
~~~~~~~~~~~~
In order to enable GitHub login you must get an OAuth client id and client
secret from GitHub and add them to:

.. code-block:: python

   GITHUB_APP_CREDENTIALS = dict(
       consumer_key='...',
       consumer_secret='...',
   )


For the GitHub integration to work with a self-signed SSL certificate you need
to set (only use this during development):

.. code-block:: python

   GITHUB_INSECURE_SSL = True

Also, for production instances, you should set the following shared secret
(note, do not use your `SECRET_KEY` for this):

.. code-block:: python

   GITHUB_SHARED_SECRET = '...'


DataCite DOI minting
~~~~~~~~~~~~~~~~~~~~
For DOI minting to work you must provide the DataCite prefix and credentials
like this:

.. code-block:: python

   PIDSTORE_DATACITE_USERNAME = '...'
   PIDSTORE_DATACITE_PASSWORD = '...'
   PIDSTORE_DATACITE_DOI_PREFIX = '10.5072'


Google Site Verification
~~~~~~~~~~~~~~~~~~~~~~~~
If you want to use Google Webmasters toolkit you can add the site verification
id in to the templates by setting the following configuration:

.. code-block:: python

   GOOGLE_SITE_VERIFICATION = ['<id1>', '<id2>', ...]


Elasticsearch
~~~~~~~~~~~~~
If you need to configure Elasticsearch to connect to an ES cluster with HTTPS
proxy using HTTP Basic authentication it can be done like this:

.. code-block:: python

   SEARCH_ELASTIC_KWARGS = dict(
       port=443,
       http_auth=('myuser', 'mypassword'),
       use_ssl=True,
       verify_certs=False,
   )
   SEARCH_ELASTIC_HOSTS = [
       dict(host='es1.example.org', **SEARCH_ELASTIC_KWARGS),
       dict(host='es2.example.org', **SEARCH_ELASTIC_KWARGS),
       dict(host='es2.example.org', **SEARCH_ELASTIC_KWARGS),
   ]


PostgreSQL, RabbitMQ, Redis
~~~~~~~~~~~~~~~~~~~~~~~~~~~
In case you want to use a remote database, broker and cache you can change the
defaults using the following configuration variables:

.. code-block:: python

   SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://dbhost/db'
   REDIS_URL = 'redis://redishost:6379'
   BROKER_URL = 'amqp://rabbitmqhost:5672/myvhost"

   ACCOUNTS_SESSION_REDIS_URL = '{0}/0'.format(REDIS_URL)
   CACHE_REDIS_URL = '{0}/0'.format(REDIS_URL)
   CELERY_RESULT_BACKEND = '{0}/1'.format(REDIS_URL)


Storage
~~~~~~~
You can configure the default storage location using the configuration
variable:

.. code-block:: python

   FIXTURES_DEFAULT_LOCATION = \
    'root://eospublic.cern.ch//eos/zenodo/prod/data/'

In case you need XRootD support, please ensure that
`XRootDPyFS <http://pythonhosted.org/xrootdpyfs/>`_ have been installed by e.g.
installing Zenodo with the ``xrootd`` extras:

.. code-block:: console

   $ pip install -e .[postgresql,xrootd]

Sentry
~~~~~~
If you would like error logging to Sentry, set the configuration variable:

.. code-block:: python

   SENTRY_DSN = 'https://user:pw@sentry.example.org/'

Theme
~~~~~
Piwik analytics can be configured with the configuration variable:

.. code-block:: python

   THEME_PIWIK_ID = 123

You can add a message to all pages, in order to show that a certain instancen
is not a production instance, e.g."

.. code-block:: python

   THEME_TAG = 'Sandbox'

Assets
~~~~~~
For non-development installation be sure to set the static file collection to
copy files instead of symlinking:

.. code-block:: python

   COLLECT_STORAGE = 'flask_collect.storage.file'


Metrics
~~~~~~~
Zenodo uses the Invenio-Metrics module to compute application KPIs at given
intervals and send it to the CERN monitoring infrastructure.

.. code-block:: python

   METRICS_XSLS_API_URL = "http://xsls-dev.cern.ch"
   METRICS_XSLS_SERVICE_ID = "myid"

StatsD
~~~~~~
Zenodo uses StatsD to measure request performance.

.. code-block:: python

   STATSD_HOST = "localhost"
   STATSD_PORT = 8125
   STATSD_PREFIX = "zenodo"

Proxy configuration
~~~~~~~~~~~~~~~~~~~
In order for Zenodo to correctly determine a client's IP address, you must set
how many proxies are in-front of the application (Zenodo production has e.g.
two proxies in front - HAproxy and Nginx):

.. code-block:: python

   WSGI_PROXIES = 2

Vocabularies
------------
Zenodo relies on external vocabularies/authorities for linking records to
funders/grants and licenses. Since some of the vocabularies can be rather big,
the actual important is done using the task queue. Hence, before executing any
of the commands below, please first start Celery (see :ref:`running`).

Licenses
~~~~~~~~
Licenses are imported from `opendefinition.org
<http://licenses.opendefinition.org>`_:

.. code-block:: console

   (zenodo)$ zenodo opendefinition loadlicenses


Funders and grants
~~~~~~~~~~~~~~~~~~
Funders are imported from `FundRef <http://www.crossref.org/fundingdata/>`_.
Currently the dataset contains more than 10.000 funders:

.. code-block:: console

   (zenodo)$ zenodo openaire loadfunders


Grants are imported from `OpenAIRE <http://api.openaire.eu/#cha_oai_pmh>`_.
Currently the full dataset contains more than 600.000 grants spread over a
handful of funders. You can harvest grants selectively from the funders you
need:

.. code-block:: console

   (zenodo)$ zenodo openaire loadgrants --setspec=FP7Projects


The ``--setspec`` option should be one of the following:

* Australian Research Council: ``ARCProjects``
* European Commission FP7: ``FP7Projects``
* European Commission Horizon 2020: ``H2020Projects``
* European Commission: ``ECProjects`` (contains both FP7Projects and
  ``H2020Projects``)
* Foundation for Science and Technology, Portugal: ``FCTProjects``
* National Health and Medical Research Council: ``NHMRCProjects``
* National Science Foundation: ``NSFProjects``
* Wellcome Trust: ``WTProjects``

"""

from __future__ import absolute_import, print_function

from .version import __version__

__all__ = ('__version__', )
