Installation
============

The easiest way to get started with Zenodo is using the provided docker image.
First checkout the source code, build all docker images and boot them up
using Docker Compose:

.. code-block:: console

    $ git clone https://github.com/zenodo/zenodo.git
    $ git checkout next
    $ docker-compose build
    $ docker-compose up


Next, create the database and an admin user:

.. code-block:: console

    $ docker-compose run web zenodo db init
    $ docker-compose run web zenodo db create
    $ docker-compose run web zenodo users create -e info@zenodo.org -a


Now visit the following URL in your browser:

.. code-block:: console

    http://<docker ip>:5000

**Dependencies**

Zenodo depends on PostgreSQL, Elasticsearch , Redis and RabbitMQ.
