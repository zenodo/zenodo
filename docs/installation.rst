..
    This file is part of Zenodo.
    Copyright (C) 2015, 2016 CERN.

    Zenodo is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Zenodo is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Zenodo; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.


.. include:: ../INSTALL.rst

Development installation
------------------------
If you prefer not to use Docker, you can install Zenodo on your box with a bit
of extra work. Note, however that Docker provides the most similar environment
to the production environment.

First check out the source code:

.. code-block:: console

    $ cd ~/src/
    $ git clone https://github.com/zenodo/zenodo.git -b master
    $ cd zenodo

Next, create a virtual environment (using virtualenvwrapper):

.. code-block:: console

    $ mkvirtualenv zenodo
    (zenodo)$

Zenodo works on both on Python 2.7 and 3.3+. However in case you need to use
the XRootD storage interface, you will need Python 2.7 as the underlying
libraries don't support Python 3.3+ yet.

Next, install Invenio extensions and Zenodo itself:

.. code-block:: console

    (zenodo)$ pip install -r requirements.developer.txt \
    --src ~/src/ --pre --exists-action i
    (zenodo)$ pip install -e .[all,postgresql]

Above command will checkout the required Invenio extensions into ``~/src/`` as
well as install Zenodo with PostgreSQL support.

.. note::

   If you already have a checkout of one or more of the extensions, it will be
   left as-is. You are responsible for ensuring that you have the latest
   changes and correct branch in each of these repositories.

Media assets
~~~~~~~~~~~~
Afterwards you need to download and build the media assets for Zenodo. This is
done like this:

.. code-block:: console

   (zenodo)$ zenodo npm
   (zenodo)$ cd ${VIRTUAL_ENV}/var/instance/static
   (zenodo)$ npm install
   (zenodo)$ zenodo collect -v
   (zenodo)$ zenodo assets build

.. note::

   For the above commands to work you need to have NodeJS, SASS, CleanCSS,
   UglifyJS and RequireJS installed:

   .. code-block:: console

      npm install -g node-sass clean-css uglify-js requirejs


Initialization
~~~~~~~~~~~~~~
Next, create the database and Elasticsearch indexes and an admin user:

.. code-block:: console

   (zenodo)$ zenodo db init
   (zenodo)$ zenodo db create
   (zenodo)$ zenodo index init
   (zenodo)$ zenodo fixtures init
   (zenodo)$ zenodo users create info@zenodo.org -a
   (zenodo)$ zenodo access allow admin-access -e info@zenodo.org

You must already have PostgreSQL, Elasticsearch 2.x, Redis and RabbitMQ for
above to work.

Demo records
~~~~~~~~~~~~
You can now load the demo records:

.. code-block:: console

   (zenodo)$ celery worker -A zenodo.celery -l INFO --purge
   (zenodo)$ zenodo fixtures loaddemorecords
   (zenodo)$ zenodo migration recordsrun
   (zenodo)$ zenodo migration reindex recid
   (zenodo)$ zenodo index run -d
