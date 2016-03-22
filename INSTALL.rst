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
