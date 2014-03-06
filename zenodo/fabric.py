# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from __future__ import absolute_import, print_function
import os
import six
from collections import OrderedDict

from fabric.api import *
from fabric.colors import cyan


def common():
    env.VIRTUAL_ENV = os.environ.get('VIRTUAL_ENV', None)
    if not env.VIRTUAL_ENV:
        abort("Please run from inside your virtual environment")
    env.DISTS = OrderedDict([
        ('invenio', dict(
            path="%(VIRTUAL_ENV)s/src/invenio",
            cmd="sdist_deploy",
        )),
        ('zenodo', dict(
            path="%(VIRTUAL_ENV)s/src/zenodo",
        ))
    ])
    env.PREFIX = "/opt/zenodo"
    env.OWNER = 'apache'


#
# Single distribution commands
#
@task
def pack_dist(path='.', cmd='sdist'):
    """  """
    path = path % env
    with cd(path):
        local('cd %(path)s; python setup.py %(cmd)s --format=gztar' % dict(
              cmd=cmd, path=path), capture=False)


@task
def upload_dist(path, name):
    ctx = {}
    ctx.update(env)
    ctx.update(dict(
        path=path % env,
        name=name,
    ))

    with cd(path):
        dist = local('cd %(path)s; python setup.py --fullname' % ctx,
                     capture=True)

        ctx['dist'] = dist

        put(
            "%(path)s/dist/%(dist)s.tar.gz" % ctx,
            "%(PREFIX)s/dist/%(dist)s.tar.gz" % ctx,
            use_sudo=True
        )


@task
def install_dist(path, with_postinstall=False):
    ctx = {}
    ctx.update(env)
    ctx.update(dict(
        path=path % env,
    ))

    dist = local('cd %(path)s; python setup.py --fullname' % ctx,
                 capture=True)

    ctx['dist'] = dist

    with cd("%(PREFIX)s/dist/" % ctx):
        sudo('%(PREFIX)s/bin/pip install %(dist)s.tar.gz'
             ' --process-dependency-links --allow-all-external '
             '--upgrade --no-deps' % ctx,
             user=env.OWNER)

    if with_postinstall:
        post_install()


#
# Multiple distribution commands
#
@task
@runs_once
def pack(name=None):
    for key, conf in dists(name):
        print(cyan("Packing %s" % key))
        pack_dist(conf['path'], cmd=conf.get('cmd', 'sdist'))


@task
@roles('web')
@parallel
def upload(name=None):
    for key, conf in dists(name):
        print(cyan("Uploading %s" % key))
        upload_dist(conf['path'], key)


@task
@roles('web')
def install(name=None):
    for key, conf in dists(name):
        print(cyan("Installing %s" % key))
        install_dist(conf['path'])


def dists(name):
    """ Iterate over distributions """
    for key, conf in six.iteritems(env.DISTS):
        if name is None or name == key:
            yield key, conf


#
# Post installation steps
#
@task
@roles('web')
def post_install():
    with cd(env.PREFIX):
        sudo("bin/inveniomanage collect" % env, user=env.OWNER)
        sudo("bin/inveniomanage apache create-config" % env, user=env.OWNER)

    sudo("/etc/init.d/celeryd restart" % env)
    sudo("/etc/init.d/httpd graceful")


@task
@roles('web')
def apache_restart():
    sudo("/etc/init.d/httpd graceful")


@task
@roles('web')
def get_password():
    run("echo 'get the password'")


#
# All combined
#
@task
def deploy(name=None):
    print(cyan(("Deploying %s" % name) if name else "Deploying all"))
    execute(get_password)
    execute(pack, name=name)
    execute(upload, name=name)
    execute(install, name=name)
