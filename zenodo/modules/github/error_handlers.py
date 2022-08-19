# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2019-2020 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Error handlers for GitHub release exceptions."""

def versioning_files_error(release, ex):
    """Handler for VersioningFileError."""
    release.model.errors = {
        'errors': ex.get_errors()[0]['message']
    }


def authentification_failed(release, ex):
    """Handler for AuthentificationFailed."""
    release.model.errors = {
        'errors': (
            'The GitHub OAuth token we have for your account is invalid or '
            'expired. Please renew your token by disconnecting and '
            'connecting your GitHub account at our "Linked accounts" settings '
            'page. You can then contact us via our support form to have this '
            'release published.'
        )
    }


def stale_data_error(release, ex):
    """Handler for StaleDataError."""
    pass


def marshmallow_error(release, ex):
    """Handler for MarshmallowFileError."""
    release.model.errors = {'errors': str(ex.errors)}


def repository_access_error(release, ex):
    """Handler for RepositoryAccessError."""
    pass


def invalid_request_error(release, ex):
    """Handler for InvalidRequestError."""
    pass


def connection_error(release, ex):
    """Handler for ConnectionError."""
    pass


def forbidden_error(release, ex):
    """Handler for ForbiddenError."""
    pass


def server_error(release, ex):
    """Handler for ServerError."""
    pass


def client_error(release, ex):
    """Handler for ClientError."""
    pass


def integrity_error(release, ex):
    """Handler for IntegrityError."""
    pass


def default_error(release, ex):
    """Default error handler acting as a fallback."""
    release.model.errors = {
        'errors': (
            'Something went wrong when we tried to publish your release. '
            'If your release has not been published within the next hour, '
            'please contact us via our support form to resolve this issue.'
        )}


def invalid_json_error(release, ex):
    """Error for invalid JSON format."""
    release.model.errors = {
        'errors': str(ex),
    }


def invalid_ref_error(release, ex):
    """Error for invalid JSON reference."""
    release.model.errors = {
        'errors': 'The license ID you have selected is not present in our '
        'system. For the available licenses please check in the following URL '
        'https://developers.zenodo.org/#licenses',
    }
