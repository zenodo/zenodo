Installation
============

Zenodo depends on PostgreSQL, Elasticsearch 2.x, Redis and RabbitMQ.

If you are only interested in running Zenodo locally, follow the Docker
installation guide below. If you plan to eventually develop Zenodo code
continue further to Development installation to find out how to set up the
local instance for easy code development.

For this guide you will need to install
`docker <https://docs.docker.com/engine/installation/>`_ along with the
`docker-compose <https://docs.docker.com/compose/>`_ tool.

Docker installation is not necessary, although highly recommended.

If you can't use docker you can run Zenodo and all of the required services
directly in your system. Take a look at
`docker-compose.yml <https://github.com/zenodo/zenodo/blob/master/docker-compose.yml/>`_
file to find out what is required and how the configuration looks like.
For development you will need to set-up and configure
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
    $ docker-compose -f docker-compose.full.yml build
    $ docker-compose -f docker-compose.full.yml up -d


.. note::

    For the purpose of this guide we will assume that all repositories are
    checked into ``~/src/`` directory.


Keep the session with the docker-compose above alive, and in a new shell
run the init script which creates the database tables, search indexes
and some data fixtures:

.. code-block:: console

    $ cd ~/src/zenodo
    $ docker-compose -f docker-compose.full.yml run --rm web bash /code/zenodo/scripts/init.sh

Now visit the following URL in your browser:

.. code-block:: console

    https://<docker ip>

.. note::

    If you're running docker on Linux or newer Mac OS X systems,
    the ``<docker ip>`` is usually the localhost. For older Mac OS X and
    Windows systems running docker through ``docker-machine``, you can find
    the IP with

    .. code-block:: console

        $ docker-machine ip <machine-name>

You can use the following web interface to inspect Elasticsearch and RabbitMQ:

- Elasticsearch: http://<docker ip>:9200/_plugin/hq/
- RabbitMQ: http://<docker ip>:15672/ (guest/guest)
- HAProxy: http://<docker ip>:8080/ (guest/guest)

Also the following ports are exposed on the Docker host:

- ``80``: HAProxy
- ``81``: Nginx
- ``443``: HAProxy
- ``444``: Nginx
- ``5000``: Zenodo
- ``5432``: PostgreSQL
- ``5672``: RabbitMQ
- ``6379``: Redis
- ``8080``: HAProxy stats
- ``9200``: Elasticsearch
- ``9300``: Elasticsearch
- ``15672``: RabbitMQ management console


Development installation
------------------------

For the development setup we will reuse the ``docker-compose.yml`` file from
the previous section to run only the essential Zenodo services (PostgreSQL,
ElasticSearch, Redis, etc.) and run the application code and Celery worker in
our virtualenv - you will want to have easy access to the code and the virtual
environment in which it will be installed.

.. note::

    Since Docker will be mapping the services to the default system
    ports on ``localhost``, make sure you are not running PostgreSQL,
    Redis, RabbitMQ or Elasticsearch on those ports in your system.

Similarly to how we previously ran ``docker-compose -f docker-compose.full.yml
up -d`` to run a "full-stack" version of Zenodo, this time we run only
four Docker containers with PostgreSQL, ElasticSearch, Redis, and RabbitMQ:

.. code-block:: console

    # NOTE: The "-d" flag runs the containers in the background
    $ docker-compose up -d

Now, create a new Python virtual environment using `virtualenvwrapper
<https://virtualenvwrapper.readthedocs.io/en/latest/>`_, in which we will
install the Zenodo application code and its dependencies:

.. code-block:: console

    $ mkvirtualenv -p python2.7 zenodo
    (zenodo)$

.. note::

    Zenodo works on both on Python 2.7 and 3.5+. However in case you need to
    use the XRootD storage interface, you will need Python 2.7 as the
    underlying libraries don't support Python 3.5+ yet.

Next, install Zenodo and code the dependencies:

.. code-block:: console

    (zenodo)$ cd ~/src/zenodo
    (zenodo)$ pip install -r requirements.txt
    (zenodo)$ pip install -e ".[all]"

Frontend assets
~~~~~~~~~~~~~~~

Next, we need to build the assets for the Zenodo application.

To compile Zenodo assets we will need to install:

* NodeJS **7.4** and NPM **4.0.5**
* Asset-building dependencies: SASS **3.8.0**, CleanCSS **3.4.19**, UglifyJS **2.7.3** and RequireJS **2.2.0**

You can install NodeJS, NPM and other dependencies using NVM (Node Version
Manager), which is similar to Python's ``pyenv``. To do that, you need to first
install NVM from `https://github.com/creationix/nvm
<https://github.com/creationix/nvm/>`_.

Once NVM is installed, set it to use NodeJS version 7.4:

.. code-block:: console

   (zenodo)$ nvm install 7.4
   (zenodo)$ nvm use 7.4
   Now using node v7.4.0 (npm v4.0.5)

Optionally, if you plan on working for a longer time with Node v7.4, you can
also set it as the default version, to avoid having to run ``nvm use ...``
every time:

.. code-block:: console

   (zenodo)$ nvm alias default 7.4

Install the npm requirements:

.. code-block:: console

   (zenodo)$ ./scripts/setup-npm.sh

The packages will be installed in your local user's NVM environment.

After you've installed the NPM packages, you can finally download and build the
frontend assets for Zenodo, by running the following script:

.. code-block:: console

   (zenodo)$ ./scripts/setup-assets.sh

Running services
~~~~~~~~~~~~~~~~

To run Zenodo locally, you will need to have some services running on your
machine. At minimum you must have PostgreSQL, Elasticsearch 7.x, Redis and
RabbitMQ.

To run only the essential services using Docker, execute the following:

.. code-block:: console

    $ cd ~/src/zenodo
    $ docker-compose up -d

This should bring up four docker nodes with PostgreSQL (db), Elasticsearch (es),
RabbitMQ (mq), and Redis (cache). Keep this shell session alive.

Initialization
~~~~~~~~~~~~~~

Now that the services are running, it's time to initialize the Zenodo database
and the ElasticSearch indexes.

Create the database, ElasticSearch indexes, messages queues and various
fixtures for licenses, grants, communities and users in a new shell session:

.. code-block:: console

   $ cd ~/src/zenodo
   $ workon zenodo
   (zenodo)$ ./scripts/init.sh

Let's also run the Celery worker on a different shell session:

.. code-block:: console

   $ cd ~/src/zenodo
   $ workon zenodo
   (zenodo)$ celery worker -A zenodo.celery -l INFO --purge

Loading data
~~~~~~~~~~~~

Next, let's load some external data (only licenses for the time being). Loading
of this demo data is done asynchronusly with Celery, but depends on internet
access since it involves harvesting external OAI-PMH or REST APIs.

Make sure you keep the session with Celery worker alive. Launch the data
loading commands in a separate shell:

.. code-block:: console

   $ cd ~/src/zenodo
   $ workon zenodo
   (zenodo)$ zenodo opendefinition loadlicenses -s opendefinition
   (zenodo)$ zenodo opendefinition loadlicenses -s spdx
   (zenodo)$ ./scripts/index.sh

Finally, run the Zenodo development server in debug mode. You can do that by
setting up the environment flag:

.. code-block:: console

    (zenodo)$ export FLASK_DEBUG=True
    (zenodo)$ zenodo run

If you go to http://localhost:5000, you should see an instance of Zenodo,
similar to the production instance at https://zenodo.org.

Badges
~~~~~~
In order for the DOI badges to work you must have the Cairo SVG library and the
DejaVu Sans font installed on your system. Please see `Invenio-Formatter
<http://pythonhosted.org/invenio-formatter/installation.html>`_ for details.
