Installation
============

Docker installation
-------------------
The easiest way to get started with Zenodo is using the provided docker image.
First checkout the source code, build all docker images and boot them up
using Docker Compose:

.. code-block:: console

    $ git clone https://github.com/zenodo/zenodo.git
    $ git checkout master
    $ docker-compose build
    $ docker-compose up

Next, create the database, indexes, fixtures and an admin user:

.. code-block:: console

    $ docker-compose run --rm web bash /code/zenodo/scripts/init.sh
    $ docker-compose run --rm statsd bash /init.sh

Next, load demo records:

.. code-block:: console

    $ docker-compose run --rm web zenodo fixtures loaddemorecords
    $ docker-compose run --rm web zenodo migration recordsrun
    $ docker-compose run --rm web zenodo index reindex --yes-i-know
    $ docker-compose run --rm web zenodo index run -d

Now visit the following URL in your browser:

.. code-block:: console

    https://<docker ip>

You can use the following web interface to inspect Elasticsearch and RabbitMQ:

- Elasticsearch: http://<docker ip>:9200/_plugin/hq/
- RabbitMQ: http://<docker ip>:15672/ (guest/guest)

Also the following ports are exposed on the Docker host:

- ``80``: Nginx
- ``443``: Nginx
- ``5000``: Zenodo
- ``5432``: PostgreSQL
- ``5601``: Kibana
- ``5672``: RabbitMQ
- ``6379``: Redis
- ``8125``: StatsD (UDP)
- ``9200``: Elasticsearch
- ``9300``: Elasticsearch
- ``15672``: RabbitMQ management console

**Dependencies**

Zenodo depends on PostgreSQL, Elasticsearch, Redis and RabbitMQ.


Development installation
------------------------
For core developers it is often faster and easier in the long run to not to use
Docker, with a bit of extra up-front work to configure your box. Note, however
that Docker provides the most similar environment to the production
environment.

First check out the source code:

.. code-block:: console

    $ cd ~/src/
    $ git clone https://github.com/zenodo/zenodo.git
    $ cd zenodo

Next, create a virtual environment (using
`virtualenvwrapper <https://virtualenvwrapper.readthedocs.io/en/latest/>`_):

.. code-block:: console

    $ mkvirtualenv zenodo
    (zenodo)$

Zenodo works on both on Python 2.7 and 3.5+. However in case you need to use
the XRootD storage interface, you will need Python 2.7 as the underlying
libraries don't support Python 3.5+ yet.

Next, install Invenio extensions and Zenodo itself:

.. code-block:: console

    (zenodo)$ pip install -r requirements.txt --src ~/src/ --pre
    (zenodo)$ pip install -e .[all,postgresql]

Above command will checkout development versions of certain Invenio extensions
into ``~/src/`` as well as install Zenodo with PostgreSQL support.

Media assets
~~~~~~~~~~~~
Afterwards you need to download and build the media assets for Zenodo. This is
done like this:

.. code-block:: console

   (zenodo)$ ./scripts/setup-assets.sh

.. note::

   For the above commands to work you need to have NodeJS, SASS, CleanCSS,
   UglifyJS and RequireJS installed:

   .. code-block:: console

      (zenodo)$ ./scripts/setup-npm.sh

   Feel free to take a peek in the scripts to see the commands being run


Initialization
~~~~~~~~~~~~~~
Next, create the database and Elasticsearch indexes and an admin user:

.. code-block:: console

   (zenodo)$ ./scripts/init.sh

You must already have PostgreSQL, Elasticsearch 2.x, Redis and RabbitMQ for
above to work.

Demo records
~~~~~~~~~~~~
You can now load the demo records (licenses, funders, grants, records):

.. code-block:: console

   (zenodo)$ celery worker -A zenodo.celery -l INFO --purge
   (zenodo)$ zenodo opendefinition loadlicenses
   (zenodo)$ zenodo fixtures loadlicenses
   (zenodo)$ zenodo openaire loadfunders \
    --source=~/src/invenio-openaire/invenio_openaire/data/fundref_registry.rdf
   (zenodo)$ zenodo fixtures loadfp6grants
   (zenodo)$ zenodo openaire loadgrants --setspec=FP7Projects
   (zenodo)$ zenodo fixtures loaddemorecords
   (zenodo)$ zenodo migration recordsrun
   (zenodo)$ zenodo migration reindex recid
   (zenodo)$ zenodo index run -d


Badges
~~~~~~
In order for the DOI badges to work you must have the Cairo SVG library and the
DejaVu Sans font installed on your system . Please see `Invenio-Formatter
<http://pythonhosted.org/invenio-formatter/installation.html>`_ for details.
