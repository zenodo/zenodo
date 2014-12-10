Installation
=============

1. About
--------

This document specifies how to install a development version of Zenodo for the
first time. Production grade deployment is not covered here.

2. Prerequisites
----------------

First follow the section "2. Prerequisites" in `First Steps with Invenio <http://invenio.readthedocs.org/en/latest/getting-started/first-steps.html#prerequisites>`_.

3. Quick start
--------------

3.1. Getting the source code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First go to GitHub and fork both Invenio and Zenodo repositories if you have
not already done so (see Step 1 in
`Fork a Repo <https://help.github.com/articles/fork-a-repo>`_):

- `Invenio <https://github.com/inveniosoftware/invenio>`_
- `Zenodo <https://github.com/zenodo/zenodo>`_

Next, clone your forks to get development versions of Invenio and Zenodo.

.. code-block:: console

    $ cd $HOME/src/
    $ git clone https://github.com/<username>/invenio.git
    $ git clone https://github.com/<username>/zenodo.git

Make sure you configure upstream remote for the repository so you can fetch
updates to the repository.

.. code-block:: console

    $ cd $HOME/src/invenio
    $ git remote add upstream https://github.com/inveniosoftware/invenio.git
    $ git fetch upstream
    $ git remote add zenodo https://github.com/zenodo/invenio.git
    $ git fetch zenodo
    $ cd $HOME/src/zenodo
    $ git remote add zenodo https://github.com/zenodo/zenodo.git
    $ git fetch zenodo


3.2 Working environment
~~~~~~~~~~~~~~~~~~~~~~~

We recommend to work using
`virtual environments <http://www.virtualenv.org/>`_ so packages are installed
in an isolated environment . ``(zenodo)$`` tells that your
*zenodo* environment is the active one.

.. code-block:: console

    $ mkvirtualenv zenodo
    (zenodo)$ # we are in the zenodo environment now and
    (zenodo)$ # can leave it using the deactivate command.
    (zenodo)$ deactivate
    $ # Now join it back, recreating it would fail.
    $ workon zenodo
    (zenodo)$ # That's all there is to know about it.

Let's create a working copy of the Invenio and Zenodo source code in the
just created environment.

.. code-block:: console

    (zenodo)$ cdvirtualenv
    (zenodo)$ mkdir src; cd src
    (zenodo)$ git-new-workdir $HOME/src/invenio/ invenio pu-zenodo
    (zenodo)$ git-new-workdir $HOME/src/zenodo/ zenodo master

By default we checkout the development branches ``master`` for Zenodo and
``pu-zenodo`` for Invenio (see :ref:`branches` for other possibilities).


3.3 Installation
~~~~~~~~~~~~~~~~
The steps for installing Zenodo are nearly identical to a normal Invenio
installation:

.. code-block:: console

    (zenodo)$ cdvirtualenv src/zenodo
    (zenodo)$ pip install -r requirements.txt --exists-action i

.. NOTE::
   The option ``--exists-action i`` for ``pip install`` is needed to ensure that
   the Invenio source code we just cloned will not be overwritten. If you
   omit it, you will be prompted about which action to take.

For development environments you should install our git commit hooks that checks
code according to our code quality standards:

.. code-block:: console

    (zenodo)$ cd $HOME/src/invenio/
    (zenodo)$ kwalitee githooks install
    (zenodo)$ cd $HOME/src/zenodo/
    (zenodo)$ kwalitee githooks install


3.4. Configuration
~~~~~~~~~~~~~~~~~~

Generate the secret key for your installation.

.. code-block:: console

    (zenodo)$ inveniomanage config create secret-key

If you are planning to develop locally in multiple environments please run
the following commands.

.. code-block:: console

    (zenodo)$ inveniomanage config set CFG_EMAIL_BACKEND flask.ext.email.backends.console.Mail
    (zenodo)$ inveniomanage config set CFG_BIBSCHED_PROCESS_USER $USER

By default the database name and username is set to ``zenodo``. You mau want to
change that especially if you have multiple local installations:

.. code-block:: console

    (zenodo)$ inveniomanage config set CFG_DATABASE_NAME <name>
    (zenodo)$ inveniomanage config set CFG_DATABASE_USER <username>

3.5. Assets
~~~~~~~~~~~

Assets in non-development mode may be combined and minified using various
filters. We need to set the path to the binaries if they are not in the
environment ``$PATH`` already.

.. code-block:: console

    # Global installation
    $ sudo npm install -g less clean-css requirejs uglify-js bower

    or
    # Local installation
    (invenio)$ inveniomanage config set LESS_BIN `find $PWD/node_modules -iname lessc | head -1`
    (invenio)$ inveniomanage config set CLEANCSS_BIN `find $PWD/node_modules -iname cleancss | head -1`
    (invenio)$ inveniomanage config set REQUIREJS_BIN `find $PWD/node_modules -iname r.js | head -1`
    (invenio)$ inveniomanage config set UGLIFYJS_BIN `find $PWD/node_modules -iname uglifyjs | head -1`


Install the external JavaScript and CSS libraries:

.. code-block:: console

    (zenodo)$ cdvirtualenv src/zenodo
    (zenodo)$ inveniomanage bower > bower.json
    (zenodo)$ bower install


``inveniomanage collect`` will create the static folder with all
the required assets (JavaScript, CSS and images) from each module static folder
and bower. ``inveniomanage assets build`` will build minified and cleaned
assets using the once that have been copied to the static folder.

.. code-block:: console

    (zenodo)$ inveniomanage config set COLLECT_STORAGE invenio.ext.collect.storage.link
    (zenodo)$ inveniomanage collect
    (zenodo)$ inveniomanage assets build


3.6. Initial data
~~~~~~~~~~~~~~~~~

Once you have everything installed you can create the database and populate it
with initial data.

.. code-block:: console

    (invenio)$ inveniomanage database init --user=root --password=$MYSQL_ROOT --yes-i-know
    (invenio)$ inveniomanage database create

3.7. Background queues (FIXME)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now you should be able to run the development server. Invenio uses
`Celery <http://www.celeryproject.org/>`_ and `Redis <http://redis.io/>`_
which must be running alongside with the web server.

.. code-block:: console

    $ # make sure that redis is running
    $ sudo service redis-server status
    redis-server is running
    $ # or start it with start
    $ sudo service redis-start start

    $ # launch celery
    $ workon zenodo
    (zenodo)$ celeryd -E -A invenio.celery.celery --workdir=$VIRTUAL_ENV

    $ # launch bibsched
    (zenodo)$ bibsched start

    $ # in a new terminal
    $ workon zenodo
    (zenodo)$ inveniomanage runserver
     * Running on http://0.0.0.0:4000/
     * Restarting with reloader


**Troubleshooting:** As a developer, you may want to use the provided
``Procfile`` with `honcho <https://pypi.python.org/pypi/honcho>`_. It
starts all the services at once with nice colors. Be default, it also runs
`flower <https://pypi.python.org/pypi/flower>`_ which offers a web interface
to monitor the *Celery* tasks.

.. code-block:: console

    (zenodo)$ pip install flower

When you have the servers running, it is possible to upload the demo records.

.. code-block:: console

    $ # in a new terminal
    $ workon zenodo
    (zenodo)$ cdvirtualenv src/zenodo
    (zenodo)$ inveniomanage demosite populate --packages=zenodo.demosite \
              -f zenodo/testsuite/demo_zenodo_record_marc_data.xml \
              -e force-recids

And you may now open your favourite web browser on
`http://0.0.0.0:4000/ <http://0.0.0.0:4000/>`_



4.4 Fetching pull requests
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    $ cd $HOME/src/invenio/
    $ vim .git/config

Add ``fetch = +refs/pull/*/head:refs/remotes/upstream/pr/*`` to the remote
``upstream``.

.. code-block:: ini

    [remote "upstream"]
        url = git://github.com/inveniosoftware/invenio.git
        fetch = +refs/heads/*:refs/remotes/upstream/*
        fetch = +refs/pull/*/head:refs/remotes/upstream/pr/*


.. code-block:: console

    $ cd $HOME/src/zenodo/
    $ vim .git/config

Add ``fetch = +refs/pull/*/head:refs/remotes/upstream/pr/*`` to the remote
``zenodo``.

.. code-block:: ini

    [remote "zenodo"]
        url = https://github.com/zenodo/zenodo.git
        fetch = +refs/heads/*:refs/remotes/upstream/*
        fetch = +refs/pull/*/head:refs/remotes/upstream/pr/*


