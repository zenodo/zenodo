Installation
============

Zenodo depends on PostgreSQL, Elasticsearch 2.x, Redis and RabbitMQ.

If you are only interested in running Zenodo locally, follow the Docker
installation guide below. If you plan to eventually develop Zenodo code you
continue further to Development installation to find out how to set up the
local instance for easy code development.

For this guide you will need to install
`docker <https://docs.docker.com/engine/installation/>`_ along with the
`docker-compose <https://docs.docker.com/compose/>`_ tool.

Docker installation is not necessary, although highly recommended.

If you can't use docker you can run Zenodo and all of the required services
directly in your system. Take a look at ``docker-compose.yml`` file to find out
what is required and how the configuration looks like.
For development you will need to set-up an configure
four services: PostgreSQL (``db``), Elasticsearch (``es``),
Redis (``cache``) and RabbitMQ (``mq``).

Docker installation
-------------------
The easiest way to run Zenodo locally is to use the provided docker-compose
configuration containing full Zenodo stack. First checkout the source code,
build all docker images and boot them up using ``docker-compose``:

.. code-block:: console

    $ cd ~/src/
    $ git clone https://github.com/zenodo/zenodo.git
    $ cd ~/src/zenodo
    $ git checkout master
    $ docker-compose build
    $ docker-compose up


.. note::

    For the purpose of this guide we will assume that all repositories are
    checked into ``~/src/`` directory.


Keep the session with the docker-compose above alive, and in a new shell
run the init script which creates the database tables, search indexes
and some data fixtures:

.. code-block:: console

    $ cd ~/src/zenodo
    $ docker-compose run --rm web bash /code/zenodo/scripts/init.sh
    $ docker-compose run --rm statsd bash /init.sh

Next, load the demo records and index them:

.. code-block:: console

    $ docker-compose run --rm web zenodo fixtures loaddemorecords
    $ docker-compose run --rm web zenodo migration recordsrun
    $ docker-compose run --rm web zenodo migration reindex -t recid
    $ docker-compose run --rm web zenodo index run -d

Now visit the following URL in your browser:

.. code-block:: console

    https://<docker ip>

.. note::

    If you're running docker on Linux or newer Mac OSX systems,
    the ``<docker ip>`` is usually the localhost. For older Mac OSX and Windows
    systems running docker through ``docker-machine``, you can find the IP with

    .. code-block:: console

        $ docker-machine ip <machine-name>

You can use the following web interface to inspect Elasticsearch and RabbitMQ:

- Elasticsearch: http://<docker ip>:9200/_plugin/hq/
- Kibana: http://<docker ip>:5601/
- RabbitMQ: http://<docker ip>:15672/ (guest/guest)
- HAProxy: http://<docker ip>:8080/ (guest/guest)

Also the following ports are exposed on the Docker host:

- ``80``: HAProxy
- ``81``: Nginx
- ``443``: HAProxy
- ``444``: Nginx
- ``5000``: Zenodo
- ``5432``: PostgreSQL
- ``5601``: Kibana
- ``5672``: RabbitMQ
- ``6379``: Redis
- ``8080``: HAProxy stats
- ``8125``: StatsD (UDP)
- ``9200``: Elasticsearch
- ``9300``: Elasticsearch
- ``15672``: RabbitMQ management console


Development installation
------------------------

For the development setup we will reuse the Zenodo docker image from
previous section to run only essential Zenodo services, and run the
application code and the Celery worker outside docker - you will want to
have easy access to the code and the virtual environment in which it will be
installed.

.. note::

    Since docker will be mapping the services to the default system
    ports on localhost, make sure you are not running PostgreSQL,
    Redis, RabbitMQ or Elasticsearch on those ports in your system.

Similarly to how we previously ran ``docker-compose up`` to run full-stack
Zenodo, this time we run only four docker nodes with the database,
Elasticsearch, Redis and RabbitMQ:

.. code-block:: console

    $ docker-compose up db es cache mq

Keep the docker-compose session above alive and in a separate shell, create a
new Python virtual environment using virtualenvwrapper
(`virtualenvwrapper <https://virtualenvwrapper.readthedocs.io/en/latest/>`_),
in which we will install Zenodo code and its dependencies:

.. code-block:: console

    $ mkvirtualenv zenodo
    (zenodo)$

.. note::

    Zenodo works on both on Python 2.7 and 3.5+. However in case you need to
    use the XRootD storage interface, you will need Python 2.7 as the
    underlying libraries don't support Python 3.5+ yet.

Next, install Zenodo and code the dependencies:

.. code-block:: console

    (zenodo)$ cd ~/src/zenodo
    (zenodo)$ pip install -r requirements.txt --src ~/src/ --pre --upgrade
    (zenodo)$ pip install -e .[all,postgresql]

.. note::

    ``--src ~/src/`` parameter will checkout the development versions of
    certain Invenio extensions into ``~/src/``.

.. note::

    Z shell users: wrap the ``.[all,postgresql]`` part in quotes:

    .. code-block:: console

        (zenodo)$ pip install -e ".[all,postgresql]"

Media assets
~~~~~~~~~~~~

Next, we need to build the assets for the Zenodo application.

To compile Zenodo assets you will need some NPM pacakges and asset building
tools: NodeJS, SASS, CleanCSS, UglifyJS and RequireJS.
The easiest way is to install them system-wide, and in the specific versions we
have pinned. You can do that by executing:

.. code-block:: console

   (zenodo)$ sudo ./scripts/setup-npm.sh

Take a look in the script above to see which commands are being run.
Since those pacakges are installed with ``-g`` flag (system-wide),
you will need to run the command above with ``sudo``.

Afterwards you need to download and build the media assets for Zenodo.
As before, there is a script which does that (this time without sudo):

.. code-block:: console

   (zenodo)$ ./scripts/setup-assets.sh

Running services
~~~~~~~~~~~~~~~~

To run Zenodo locally, you will need to have some services runninig on your
machine.
At minimum you must have PostgreSQL, Elasticsearch 2.x, Redis and RabbitMQ.
You can either install all of those from your system package manager and run
them directly or better - use the provided docker image as before.

**The docker image is the recommended method for development.**

.. note::

   If you run the services locally, make sure you're running
   Elasticsearch **2.x**. Elasticsearch **5.x** is NOT yet supported.


To run only the essential services using docker, execute the following:

.. code-block:: console

    $ cd ~/src/zenodo
    $ docker-compose up db es mq cache

This should bring up four docker nodes with PostgreSQL (db) Elasticsearch (es),
RabbitMQ (mq), and Redis (cache). Keep this shell session alive.

Initialization
~~~~~~~~~~~~~~
Now that the services are running, it's time to initialize the Zenodo database
and the Elasticsearch index.

Create the database and Elasticsearch indices in a new shell session:

.. code-block:: console

   $ cd ~/src/zenodo
   $ workon zenodo
   (zenodo)$ ./scripts/init.sh

Demo records
~~~~~~~~~~~~
Next, load some demo data (licenses, funders, grants, records).
Loading of the demo data is done asynchronusly with Celery.
To do that, you need to first run a Celery worker:

.. code-block:: console

   $ cd ~/src/zenodo
   $ workon zenodo
   (zenodo)$ celery worker -A zenodo.celery -l INFO --purge

Keep the session with Celery worker alive.
Launch the data loading scripts in a separate shell:

.. code-block:: console

   $ cd ~/src
   $ git clone https://github.com/inveniosoftware/invenio-openaire.git
   $ cd zenodo
   $ workon zenodo
   (zenodo)$ zenodo opendefinition loadlicenses
   (zenodo)$ zenodo openaire loadfunders \
    --source=$HOME/src/invenio-openaire/invenio_openaire/data/fundref_registry.rdf
   (zenodo)$ zenodo openaire loadgrants --setspec=FP7Projects
   (zenodo)$ zenodo fixtures loaddemorecords
   (zenodo)$ zenodo migration recordsrun
   (zenodo)$ zenodo migration reindex -t recid
   (zenodo)$ zenodo index run -d

Finally, run the Zenodo application:

.. code-block:: console

    (zenodo)$ zenodo run

If you go to http://localhost:5000, you should see an instance of Zenodo,
similar to the production instance at https://zenodo.org

.. note::

    When running the development server, it's sometimes convenient to run
    it in ``debug`` mode. You can do that by setting up the evironment flag:

    .. code-block:: console

        (zenodo)$ export FLASK_DEBUG=True
        (zenodo)$ zenodo run  --reload --with-threads

    Additionally, the flags ``--reload`` (already on when in debug mode)
    and ``--with-threads`` which allows you to have the application reload
    automatically to any detected changes in the code as well as run the
    development server with multithreading (see ``zenodo run --help``).

Badges
~~~~~~
In order for the DOI badges to work you must have the Cairo SVG library and the
DejaVu Sans font installed on your system . Please see `Invenio-Formatter
<http://pythonhosted.org/invenio-formatter/installation.html>`_ for details.
