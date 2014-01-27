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

depends_on = []


def info():
    return "OpenAIRE initial upgrade"


def do_upgrade():
    """
    Initial OpenAIRE upgrade
    """
    tables = [x[0] for x in run_sql("SHOW TABLES;")]

    # Remove old migration table (from before invenio upgrader was integrated
    # into Invenio).
    if 'migrations' in tables:
        run_sql("DROP TABLE migrations")

    # Create tables if they don't exists.
    if 'OpenAIREauthorships' not in tables:
        run_sql("""
            CREATE TABLE IF NOT EXISTS OpenAIREauthorships (
              uid int(15) NOT NULL,
              publicationid varchar(30) NOT NULL,
              authorship varchar(255) NOT NULL,
              UNIQUE (uid, publicationid, authorship),
              KEY (uid, publicationid),
              KEY (uid, authorship),
              KEY (authorship)
            ) ENGINE=MyISAM;
            """)

    if 'OpenAIREkeywords' not in tables:
        run_sql("""
            CREATE TABLE IF NOT EXISTS OpenAIREkeywords (
              uid int(15) NOT NULL,
              publicationid varchar(30) NOT NULL,
              keyword varchar(255) NOT NULL,
              KEY (uid, publicationid),
              KEY (uid, keyword),
              KEY (keyword)
            ) ENGINE=MyISAM;
            """)

    if 'eupublication' not in tables:
        run_sql("""
            CREATE TABLE IF NOT EXISTS eupublication (
              publicationid varchar(255) NOT NULL,
              projectid int(15) NOT NULL,
              uid int(15) NOT NULL,
              id_bibrec int(15) NULL default NULL,
              UNIQUE KEY (publicationid, projectid, uid),
              KEY (publicationid),
              KEY (projectid),
              KEY (uid),
              KEY (id_bibrec)
            ) ENGINE=MyISAM;
            """)

    if 'pgreplayqueue' not in tables:
        run_sql("""
            CREATE TABLE IF NOT EXISTS pgreplayqueue (
              id int(15) unsigned NOT NULL auto_increment,
              query longblob,
              first_try datetime NOT NULL default '0000-00-00',
              last_try datetime NOT NULL default '0000-00-00',
              PRIMARY KEY (id)
            ) ENGINE=MyISAM;
            """)

    # Remove old migration code from installation directory.
    try:
        import os
        import shutil
        from invenio.config import CFG_PREFIX

        files = [
            "bin/inveniomigrate",
            "lib/python/invenio/inveniomigrate.pyc",
            "lib/python/invenio/inveniomigrate.py",
            "lib/python/invenio/inveniocfg_migrate.pyc",
            "lib/python/invenio/inveniocfg_migrate.py",
        ]

        dirs = [
            "lib/python/invenio/migrations"
        ]

        for f in files:
            f = os.path.join(CFG_PREFIX, f)
            if os.path.exists(f):
                os.remove(f)

        for d in dirs:
            d = os.path.join(CFG_PREFIX, d)
            if os.path.exists(d):
                shutil.rmtree(d)
    except ImportError, e:
        pass

def estimate():
    return 1
