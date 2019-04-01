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

For the development setup we will reuse the Zenodo docker image from
previous section to run only essential Zenodo services, and run the
application code and the Celery worker outside docker - you will want to
have easy access to the code and the virtual environment in which it will be
installed.

.. note::

    Since docker will be mapping the services to the default system
    ports on localhost, make sure you are not running PostgreSQL,
    Redis, RabbitMQ or Elasticsearch on those ports in your system.

Similarly to how we previously ran
``docker-compose -f docker-compose.full.yml up -d`` to run full-stack
Zenodo, this time we run only four docker nodes with the database,
Elasticsearch, Redis and RabbitMQ:

.. code-block:: console

    $ docker-compose up -d

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
    (zenodo)$ pip install -e .[all,postgresql,elasticsearch2]

.. note::

    ``--src ~/src/`` parameter will checkout the development versions of
    certain Invenio extensions into ``~/src/``.

.. note::

    Z shell users: wrap the ``.[all,postgresql,elasticsearch2]`` part in quotes:

    .. code-block:: console

        (zenodo)$ pip install -e ".[all,postgresql,elasticsearch2]"

Media assets
~~~~~~~~~~~~

Next, we need to build the assets for the Zenodo application.

To compile Zenodo assets we will need to install:

* NodeJS **7.4** and NPM **4.0.5**

* Asset-building dependencies: SASS **3.8.0**, CleanCSS **3.4.19**, UglifyJS **2.7.3** and RequireJS **2.2.0**

If you system packages provide NodeJS and NPM in the versions listed above, you
can install the asset tools system-wide (with ``sudo``), by executing:

.. code-block:: console

   (zenodo)$ sudo ./scripts/setup-npm.sh

Take a look in the script above to see which commands are being run.
Use of ``sudo`` is required because of the ``-g`` flag for global installation.

Alternatively, you can install NodeJS, NPM and other dependencies using
NVM (node version manager), which is similar to Python's virtualenv.

To do that, you need to first install NVM from
`https://github.com/creationix/nvm <https://github.com/creationix/nvm/>`_
or from your OS-specific package repository:

* NVM on `Arch Linux AUR <https://aur.archlinux.org/packages/nvm/>`_

* Brew on OS X: ``brew install nvm``

Note: If you install NVM from system packages, you still need to source it
in your ``.bashrc`` or ``.zshrc``. Refer to NVM repository for more details.

Once NVM is installed, set it to use NodeJS in version 7.4:

.. code-block:: console

   (zenodo)$ nvm use 7.4
   Now using node v7.4.0 (npm v4.0.5)

As before, install the npm requirements, this time without ``sudo``:

.. code-block:: console

   (zenodo)$ ./scripts/setup-npm.sh

the packages will be installed in your local user's NVM environment.

After you've installed the NPM packages system-wide or with NVM, you can
finally download and build the media assets for Zenodo. There is a script
which does that:

.. code-block:: console

   (zenodo)$ ./scripts/setup-assets.sh

Running services
~~~~~~~~~~~~~~~~

To run Zenodo locally, you will need to have some services running on your
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
    $ docker-compose up -d

This should bring up four docker nodes with PostgreSQL (db), Elasticsearch (es),
RabbitMQ (mq), and Redis (cache). Keep this shell session alive.

Initialization
~~~~~~~~~~~~~~
Now that the services are running, it's time to initialize the Zenodo database
and the Elasticsearch index.

Create the database, Elasticsearch indices, messages queues and various
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

.. note::

    Here we assume all four services (db, es, mq, cache) are bound to localhost
    (see `zenodo/config.py <https://github.com/zenodo/zenodo/blob/master/zenodo/config.py/>`_).
    If you fail to connect those services, it is likely
    you are running docker through ``docker-machine`` and those services are
    bound to other IP addresses. In this case, you can redirect localhost ports
    to docker ports as follows.

    ``ssh -L 6379:localhost:6379 -L 5432:localhost:5432 -L 9200:localhost:9200 -L 5672:localhost:5672 docker@$(docker-machine ip)``

    The problem usually occurs among Mac and Windows users. A better solution
    is to install the native apps `Docker for Mac <https://docs.docker.com/docker-for-mac/>`_
    or `Docker for Windows <https://docs.docker.com/docker-for-windows/>`_
    (available since Docker v1.12) if possible,
    which binds docker to localhost by default.

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
