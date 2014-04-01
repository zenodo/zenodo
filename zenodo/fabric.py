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
from fabric.contrib.console import confirm


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
            cmd="sdist_deploy",
        ))
    ])
    env.PREFIX = "/opt/zenodo"
    env.OWNER = 'apache'
    env.HAPROXY_BACKENDS = {}


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
def install_dist(path, with_postinstall=False, with_deps=False):
    ctx = {}
    ctx.update(env)
    ctx.update(dict(
        path=path % env,
        deps='--no-deps' if not with_deps else ''
    ))

    dist = local('cd %(path)s; python setup.py --fullname' % ctx,
                 capture=True)
    name = local('cd %(path)s; python setup.py --name' % ctx,
                 capture=True)

    ctx['dist'] = dist
    ctx['name'] = name

    with cd("%(PREFIX)s/src/" % ctx):
        with settings(warn_only=True):
            sudo('%(PREFIX)s/bin/pip uninstall -y %(name)s' % ctx,
                 user=env.OWNER)
            sudo('rm -Rf %(dist)s' % ctx, user=env.OWNER)
        sudo('tar -xzvf ../dist/%(dist)s.tar.gz' % ctx, user=env.OWNER)

    with cd("%(PREFIX)s/src/%(dist)s" % ctx):
        sudo('%(PREFIX)s/bin/python setup.py develop' % ctx, user=env.OWNER)

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
def install(name=None, with_deps=False):
    for key, conf in dists(name):
        print(cyan("Installing %s" % key))
        install_dist(conf['path'], with_deps=with_deps)


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
        sudo('bin/pip install requests==1.2.3'
             ' --upgrade' % env,
             user=env.OWNER)
        sudo("bin/inveniomanage collect" % env, user=env.OWNER)
        sudo("bin/inveniomanage apache create-config" % env, user=env.OWNER)


@task
@roles('web')
def get_password():
    run("echo 'get the password'")


#
# All combined
#
@task
def deploy(name=None, quite=False, with_deps=True):
    print(cyan(("Deploying %s" % name) if name else "Deploying all"))
    if quite:
        execute(get_password)

    if (quite or confirm(cyan("Pack project?"))):
        execute(pack, name=name)

    if (quite or confirm(cyan("Upload project?"))):
        if not quite:
            execute(get_password)
        execute(upload, name=name)

    for h in env.roledefs['web']:
        if h == env.get('BIBSCHED_HOST', '') and \
           (quite or confirm(cyan("Stop bibsched?"))):
            with settings(host_string=h):
                sudo("%(PREFIX)s/bin/bibsched stop" % env,
                     user=env.OWNER)
        if (quite or confirm(cyan("Stop celery?"))):
            execute(celery_stop, hosts=[h], )

        if h in env.get('HAPROXY_BACKENDS', {}):
            if quite or confirm(cyan("Set %s in maintenance mode?" % h)):
                execute(haproxy_disable_server, h, hosts=env.roledefs['lb'],)

        if quite or confirm(cyan("Install?")):
            execute(install, hosts=[h], name=name, with_deps=with_deps)

        if quite or confirm(cyan("Run post install?")):
            execute(post_install, hosts=[h])

        if quite or confirm(cyan("Restart Apache?")):
            execute(apache_restart, hosts=[h], )

        if h in env.get('HAPROXY_BACKENDS', {}):
            if quite or confirm(cyan("Set %s in production mode?" % h)):
                execute(haproxy_enable_server, h, hosts=env.roledefs['lb'],)

        if h == env.get('BIBSCHED_HOST', '') and \
           (quite or confirm(cyan("Run upgrader?"))):
            with settings(host_string=h):
                sudo("%(PREFIX)s/bin/inveniomanage upgrader run" % env,
                     user=env.OWNER)
        if h == env.get('BIBSCHED_HOST', '') and \
           (quite or confirm(cyan("Start bibsched?"))):
            with settings(host_string=h):
                sudo("%(PREFIX)s/bin/bibsched start" % env,
                     user=env.OWNER)
        if quite or confirm(cyan("Start celery?")):
            execute(celery_start, hosts=[h])


#
# Boostrap
#
@task
@roles('web')
def bootstrap():
    ctx = {}
    ctx.update(env)
    ctx.update(dict(
        dirname=os.path.dirname(env.PREFIX),
        basename=os.path.basename(env.PREFIX),
    ))

    with cd(ctx['dirname']):
        sudo("mkdir %s" % ctx['basename'])
        sudo("chown %(OWNER)s:%(OWNER)s %(basename)s" % ctx)
        sudo("virtualenv %(basename)s" % ctx, user=env.OWNER)

    with cd(ctx['PREFIX']):
        sudo("mkdir dist", user=env.OWNER)
        sudo("mkdir src", user=env.OWNER)
        sudo("mkdir -p etc/certs", user=env.OWNER)
        sudo("bin/pip install setuptools pip --upgrade", user=env.OWNER)
        sudo("bin/pip install ipython ipdb importlib --upgrade",
             user=env.OWNER)

    with cd(os.path.join(ctx['PREFIX'], 'var')):
        sudo("mkdir run", user=env.OWNER)
        sudo("mkdir dbdump", user=env.OWNER)
        sudo("mkdir cache", user=env.OWNER)
        sudo("mkdir log", user=env.OWNER)
        sudo("mkdir tmp-shared", user=env.OWNER)
        sudo("mkdir tmp", user=env.OWNER)
        sudo("mkdir -p data/deposit/storage", user=env.OWNER)
        sudo("mkdir -p data/files", user=env.OWNER)
        sudo("mkdir -p data/deposit", user=env.OWNER)
        sudo("mkdir invenio.base-instance", user=env.OWNER)

    with cd(os.path.join(ctx['PREFIX'], 'var/invenio.base-instance')):
        sudo("mkdir run", user=env.OWNER)
        sudo("mkdir docs", user=env.OWNER)
        sudo("mkdir static", user=env.OWNER)
        sudo("mkdir apache", user=env.OWNER)

    deploy(with_deps=True)
    post_install()


#
# HAProxy
#
@task
@roles('lb')
def haproxy_disable_server(servername):
    haproxy_server_action(servername, action='disable')


@task
@roles('lb')
def haproxy_enable_server(servername):
    haproxy_server_action(servername, action='enable')


def haproxy_server_action(servername, action='disable'):
    servers = env.get('HAPROXY_BACKENDS', {}).get(servername, [])

    if servers:
        if action == 'disable':
            puts(cyan(">>> Disabling %s ..." % ", ".join(servers)))
        else:
            puts(cyan(">>> Enabling %s ..." % ", ".join(servers)))
    else:
        puts(cyan(">>> No servers to %s..." % action))

    cmd = ";".join([
        """echo "%s server %s" | socat stdio /var/lib/haproxy/stats""" %
        (action, x) for x in servers])

    sudo(cmd)


#
# Apache
#
@task
@roles('web')
def apache_restart():
    sudo("/etc/init.d/httpd configtest")
    sudo("/etc/init.d/httpd graceful")


@task
@roles('web')
def apache_start():
    sudo("/etc/init.d/httpd start")


@task
@roles('web')
def apache_stop():
    sudo("/etc/init.d/httpd stop")


@task
@roles('web')
def celery_start():
    sudo("/etc/init.d/celeryd start")


@task
@roles('web')
def celery_stop():
    sudo("/etc/init.d/celeryd stop")
