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

    (zenodo)$ pip install -r requirements.txt --src ~/src/ --pre --exists-action i
    (zenodo)$ pip install -e .[all,postgresql]

Above command will checkout development versions of certain Invenio extensions
into ``~/src/`` as well as install Zenodo with PostgreSQL support.

.. note::

   If you already have a checkout of one or more of the extensions, it will be
   left as-is. You are responsible for ensuring that you have the latest
   changes and correct branch in each of these repositories.

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
You can now load the demo records:

.. code-block:: console

   (zenodo)$ celery worker -A zenodo.celery -l INFO --purge
   (zenodo)$ zenodo fixtures loaddemorecords
   (zenodo)$ zenodo migration recordsrun
   (zenodo)$ zenodo migration reindex recid
   (zenodo)$ zenodo index run -d


Badges
~~~~~~
In order for the DOI badges to work you must have the Cairo SVG library and the
DejaVu Sans font installed on your system . Please see `Invenio-Formatter
<http://pythonhosted.org/invenio-formatter/installation.html>`_ for details.
