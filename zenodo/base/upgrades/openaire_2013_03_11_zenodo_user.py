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

import warnings
from invenio.legacy.dbquery import run_sql
from invenio.utils.text import wait_for_user


depends_on = ['openaire_2013_03_07_zenodo_collections']


def info():
    return "Migration of Orphan users"


def do_upgrade():
    """ Implement your upgrades here  """
    from invenio.openaire_deposit_config import CFG_OPENAIRE_DEPOSIT_PATH
    import shutil
    import os

    # Remove all but the admin user
    res = run_sql("SELECT id FROM user WHERE email='lars.holm.nielsen@cern.ch'")

    run_sql("DELETE FROM user WHERE id!=%s", res[0])
    run_sql("DELETE FROM user_accROLE WHERE id_user!=%s", res[0])
    run_sql("DELETE FROM user_bskBASKET")
    run_sql("DELETE FROM user_msgMESSAGE")
    run_sql("DELETE FROM user_query")
    run_sql("DELETE FROM user_usergroup")

    # Set all auto-complete authorships and keywords to the admin user
    run_sql("UPDATE IGNORE OpenAIREauthorships SET uid=176, publicationid=''")
    run_sql("UPDATE IGNORE OpenAIREkeywords SET uid=176, publicationid=''")

    # Remove all depositions from old users
    run_sql("DELETE FROM eupublication")


def estimate():
    """  Estimate running time of upgrade in seconds (optional). """
    return 5


def pre_upgrade():
    """  Run pre-upgrade checks (optional). """
    try:
        from invenio.openaire_deposit_config import CFG_OPENAIRE_DEPOSIT_PATH
        import shutil
    except ImportError:
        raise RuntimeError("This does not seem to be an OpenAIRE installation. Cannot import 'openaire_deposit_config'.")


def post_upgrade():
    """  Run post-upgrade checks (optional). """
    # Example of issuing warnings:
    # warnings.warn("A continuable error occurred")
