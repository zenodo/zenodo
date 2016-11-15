# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Click command-line interface for GitHub management."""

from __future__ import absolute_import, print_function

import click
from flask.cli import with_appcontext
from invenio_accounts.models import User
from invenio_db import db
from invenio_github.api import GitHubAPI
from invenio_github.models import Repository
from sqlalchemy.orm.exc import NoResultFound


@click.group()
def github():
    """Management commands for GitHub."""


def resolve_user(user_param):
    """Resolve user from CLI input parameter (email or User ID)."""
    if user_param is None:
        return
    if '@' in user_param:  # Try to resolve as email
        try:
            user = User.query.filter_by(email=user_param.strip()).one()
        except NoResultFound:
            raise Exception("User {0} not found.".format(user_param))
    else:
        try:
            user_id = int(user_param)
            user = User.query.get(user_id)
        except ValueError:
            raise Exception("User parameter must be either an email or ID")
        if user is None:
            raise Exception("User {0} not found.".format(user_param))
    return user


def resolve_repo(repo_param):
    """Resolve GitGub repository CLI input parameter (name or GitHub ID)."""
    if repo_param is None:
        return
    try:
        if '/' in repo_param:
            repo = Repository.query.filter_by(name=repo_param).one()
        else:
            try:
                github_id = int(repo_param)
            except ValueError:
                raise Exception('GitHub repository parameter must be either'
                                ' a name or GitHub ID')
            repo = Repository.query.filter_by(github_id=github_id).one()
    except NoResultFound:
        raise Exception("Repository {0} not found.".format(repo_param))
    return repo


def resolve_repos(repo_params):
    """Resolve multiple GitHub repository param with 'multiple' flag."""
    return tuple(resolve_repo(p) for p in repo_params)


def verify_email(user):
    """Check if user's GitHub and account emails match."""
    gha = GitHubAPI(user_id=user.id)
    gh_email = gha.api.me().email
    if gh_email == user.email:
        click.confirm("Warning: User's GitHub email ({0}) does not match"
                      " the account's ({1}). Continue?".format(gh_email,
                                                               user.email),
                      abort=True)


@github.command('list')
@click.argument('user')
@click.option('--sync', '-s', is_flag=True,
              help='Sync the repository prior to listing.')
@click.option('with_all', '--all', '-a', is_flag=True,
              help='List all repositories available.')
@click.option('skip_email', '--skip-email-verification', '-E', is_flag=True,
              help="Skip GitHub email verification.")
@with_appcontext
def repo_list(user, sync, with_all, skip_email):
    """List user's repositories hooks.

    Lists repositories currently `enabled` by the user.
    If `--all` flag is specified, lists full list of repositories from remote
    account extra data. For best result `--all` should be used with `--sync`,
    so that the GitHub information is fresh. Positional argument USER can be
    either an email or user ID.

    Examples:

      github list foo@bar.baz

      github list 12345 --sync --all
    """
    user = resolve_user(user)
    gha = GitHubAPI(user_id=user.id)
    if not skip_email:
        verify_email(user)
    if sync:
        gha.sync(hooks=True, async_hooks=False)  # Sync hooks asynchronously
        db.session.commit()
    if with_all:
        repos = gha.account.extra_data['repos']
        click.echo("User has {0} repositories in total.".format(len(repos)))
        for gid, repo in repos.items():
            click.echo(' {name}:{gid}'.format(name=repo['full_name'], gid=gid))

    repos = Repository.query.filter(Repository.user_id == user.id,
                                    Repository.hook.isnot(None))
    click.echo("User has {0} enabled repositories.".format(repos.count()))
    for r in repos:
        click.echo(" {0}".format(r))


def move_repository(repo, gha_old_user, gha_new_user):
    """Transfer repository model and hook from one user to another."""
    gha_old_user.remove_hook(repo.github_id, repo.name)
    gha_new_user.create_hook(repo.github_id, repo.name)
    db.session.commit()


@github.command()
@click.argument('old_user')
@click.argument('new_user')
@click.option('skip_email', '--skip-email-verification', '-E', is_flag=True,
              help="Skip GitHub email verification.")
@click.option('--yes-i-know', is_flag=True, default=False,
              help='Suppress the confirmation prompt.')
@with_appcontext
def transfer(old_user, new_user, skip_email, yes_i_know):
    """Transfer all repositories from OLD_USER to NEW_USER and register hooks.

    Values of OLD_USER and NEW_USER can be either emails or user IDs.

    Examples:

      github transfer user1@foo.org user2@baz.bar

      github transfer 1234 4567
    """
    old_user = resolve_user(old_user)
    new_user = resolve_user(new_user)
    repos = Repository.query.filter_by(user_id=old_user.id)
    prompt_msg = 'This will change the ownership for {0} repositories' \
        '. Continue?'.format(repos.count())
    if not (yes_i_know or click.confirm(prompt_msg)):
        click.echo('Aborted.')

    gha_new = GitHubAPI(user_id=new_user.id)
    gha_old = GitHubAPI(user_id=old_user.id)

    if not skip_email:
        verify_email(new_user)
        verify_email(old_user)
    for repo in repos:
        move_repository(repo, gha_old, gha_new)


@github.command()
@click.argument('user')
@click.argument('repos', nargs=-1)
@click.option('skip_email', '--skip-email-verification', '-E', is_flag=True,
              help="Skip GitHub email verification.")
@click.option('--yes-i-know', is_flag=True, default=False,
              help='Suppress the confirmation prompt.')
@with_appcontext
def assign(user, repos, skip_email, yes_i_know):
    """Assign an already owned repository to another user.

    First argument, USER, is the user to whom the repository will be assigned.
    Value of USER can be either the email or user's ID.
    Arguments REPOS specify one or more repositories, each can be either a
    repository names or a repository GitHub IDs.

    Examples:

        Assign repository 'foobar-org/repo-name' to user 'user1@foo.org':

      github assign user1@foo.org foobar-org/repo-name

        Assign three GitHub repositories to user with ID 999:

      github assign 999 15001500 baz-org/somerepo 12001200
    """
    user = resolve_user(user)
    repos = resolve_repos(repos)
    prompt_msg = 'This will change the ownership for {0} repositories' \
        '. Continue?'.format(len(repos))
    if not (yes_i_know or click.confirm(prompt_msg)):
        click.echo('Aborted.')
        return

    gha_new = GitHubAPI(user_id=user.id)
    if not skip_email:
        verify_email(user)
    for repo in repos:
        gha_prev = GitHubAPI(user_id=repo.user_id)
        move_repository(repo, gha_prev, gha_new)


@github.command()
@click.argument('user')
@click.option('--hooks', default=False, type=bool,
              help='Synchronize with hooks (Warning: slower)')
@click.option('--async-hooks', default=False, type=bool,
              help='Synchronize hooks asynchronously (--hooks required)')
@click.option('skip_email', '--skip-email-verification', '-E', is_flag=True,
              help="Skip GitHub email verification.")
@with_appcontext
def sync(user, hooks, async_hooks, skip_email):
    """Sync user's repositories.

    USER can be either an email or user ID.

    Examples:

      github sync foo@bar.baz

      github sync 999
    """
    user = resolve_user(user)
    gh_api = GitHubAPI(user_id=user.id)
    gh_api.sync(hooks=hooks, async_hooks=async_hooks)
    if not skip_email:
        verify_email(user)
    db.session.commit()


@github.command()
@click.argument('user')
@click.argument('repo')
@click.option('skip_email', '--skip-email-verification', '-E', is_flag=True,
              help="Skip GitHub email verification.")
@click.option('--yes-i-know', is_flag=True, default=False,
              help='Suppress the confirmation prompt.')
@with_appcontext
def createhook(user, repo, skip_email, yes_i_know):
    """Create the hook in repository for given user.

    USER can be either an email or a user ID.
    REPO can be either the repository name
    (e.g. `some-organization/some-repository`) or its GitHub ID.

    Examples:

      github createhook abc@foo.bar foobar-org/foobar-repo

      github createhook 12345 55555
    """
    user = resolve_user(user)
    repo = resolve_repo(repo)
    if repo.user:
        click.secho('Hook is already installed for {user}'.format(
            user=repo.user), fg='red')
        return

    msg = "Creating a hook for {user} and {repo}. Continue?".format(
        user=user, repo=repo)
    if not (yes_i_know or click.confirm(msg)):
        click.echo('Aborted.')

    gha = GitHubAPI(user_id=user.id)
    if not skip_email:
        verify_email(user)
    gha.create_hook(repo.github_id, repo.name)
    db.session.commit()


@github.command()
@click.argument('repo')
@click.option('--user', '-u', help='Attempt to remove hook using given user')
@click.option('skip_email', '--skip-email-verification', '-E', is_flag=True,
              help="Skip GitHub email verification.")
@click.option('--yes-i-know', is_flag=True, default=False,
              help='Suppress the confirmation prompt.')
@with_appcontext
def removehook(repo, user, skip_email, yes_i_know):
    """Remove the hook from GitHub repository.

    Positional argment REPO can be either the repository name, e.g.
    `some-organization/some-repository` or its GitHub ID.
    Option '--user' can be either an email or a user ID.

    Examples:

      github removehook foobar-org/foobar-repo

      github removehook 55555 -u foo@bar.baz
    """
    repo = resolve_repo(repo)
    if not repo.user and not user:
        click.secho("Repository doesn't have an owner, please specify a user.")
        return

    if user:
        user = resolve_user(user)
        if not repo.user:
            click.secho('Warning: Repository is not owned by any user.',
                        fg='yellow')
        elif repo.user != user:
            click.secho('Warning: Specified user is not the owner of this'
                        ' repository.', fg='yellow')
    else:
        user = repo.user

    if not skip_email:
        verify_email(user)

    msg = "Removing the hook for {user} and {repo}. Continue?".format(
        user=user, repo=repo)
    if not (yes_i_know or click.confirm(msg)):
        click.echo('Aborted.')
        return

    gha = GitHubAPI(user_id=user.id)
    gha.remove_hook(repo.github_id, repo.name)
    db.session.commit()
