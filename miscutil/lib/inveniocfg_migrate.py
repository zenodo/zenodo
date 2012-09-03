# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2008, 2009, 2010, 2011, 2012 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


"""
Invenio migration engine.

Usage (via inveniocfg)::

  inveniocfg --migrate-create=~/src/invenio/modules/miscutil/migrations/
  inveniocfg --migrate-history
  inveniocfg --migrate-show
  inveniocfg --migrate

Recommendations for writing migrations
--------------------------------------

 * A migration must be self-contained. If it depends on other Invenio modules,
   then their API must be very stable and backwards-compatible. Otherwise when
   a migration is applied two years later, the Invenio function might have
   evolved and the migration will fail.
 * Once a migration have been committed to master, no fiddling is allowed
   afterwards. If you want to correct a mistake, make a new migration instead.
 * All migrations must depend on a previous migration (except for your first
   migration.
 * The first migration should be empty and named 'xxxxxx_baseline.py'
 * For every software release, make a 'xxxxxx_baseline_xyz.py' that
   depends on all migrations between the previous baseline and the new, so
   future migration can depend on this baseline.

Engine notes
------------
Invenio specific parts (basically db access) have been factored out in the
subclass InvenioMigrator.

Migration dependency graph
--------------------------
The migrations form a *dependency graph* that must be without cycles (i.e. a DAG).
The migration engine supports having several independent graphs (you normally
want one graph for Invenio and one for your overlay).

The migration engine will run migrations in topological order (i.e migrations
will be run respecting the dependency graph). The engine will detect cycles in
the graph and will refuse to run any migrations until the cycles have been
broken.

Migration modules
-----------------
Migrations are implemented as normal Python modules. They must contain a class
Migration (which inherits from InvenioMigration), and implement the forward()
method.

The migration engine expects Invenio migrations are located in
invenio.migrations and can be found in CFG_PREFIX/lib/python/invenio/
"""

import os

from invenio.dbquery import run_sql
from invenio.config import CFG_PREFIX


MIGRATION_TEMPLATE = """# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2008, 2009, 2010, 2011, 2012 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from invenio.inveniocfg_migrate import InvenioMigration, run_sql_ignore
from invenio.dbquery import run_sql

class Migration( InvenioMigration ):
    \"\"\" Short description of migration \"\"\"

    repository = 'invenio'
    \"\"\" Repository name \"\"\"

    depends_on = ['baseline']
    \"\"\" A migration must depend on at least one previous migration \"\"\"

    def forward(self):
        \"\"\" Put your run_sql queries here \"\"\"
        pass
"""


class InvenioMigration(object):
    """
    Base class for a migration. Represents a vertex in the migration
    dependency graph.
    """

    depends_on = []
    """
    List of other migrations that this migration depends on. This represents
    edges in the migration dependency graph.
    """

    repository = 'invenio'
    """
    Name of the graph - this allows you to have two independent graphs.
    """

    def get_doc(self):
        """ Get first line of documentation in migration class """
        try:
            return " (%s)" % self.__class__.__doc__.split("\n")[0].strip()
        except Exception:
            return ''

    def forward(self):
        """ The migration steps are implemented in this method. """
        raise RuntimeError("Forward method not implemented")


class Migrator(object):
    """
    Base class responsible for loading and executing migrations

    A note on cross graph dependencies: A migration is uniquely identified
    by it's id (part of the filename). This means we do not get into
    a situation where a migration id will exist in two repositories. One
    repository will simply overwrite the other on install.
    """

    def __init__(self, path, package):
        """
        @param path: Path to folder with migration.
        @param package: Name of package with migrations.
        """
        self._path = path
        self._package = package
        self.migrations = None
        self.history = {}
        self.ordered_history = []

    def apply(self, migration):
        """ Main function for applying a migration """
        migration.forward()
        self.register_success(migration)

    def register_success(self, migration):
        """ Register a successful migration (must be implemented by subclass) """
        raise NotImplementedError()

    def load_history(self):
        """ Load migration history from database table (must be implemented by subclass) """
        raise NotImplementedError()

    def load_migration(self, mod_id):
        """
        Load Python migration module

        Migration modules are all located in invenio.migrations.<name>
        and must have a class Migration in the module.
        """
        module = '%s.%s' % (self._package, mod_id)
        try:
            mod = __import__(module, globals(), locals(), ['Migration'])
            return mod.Migration()
        except ImportError:
            raise Exception("Cannot import migration %s" % module)

    def find_migrations(self):
        """
        Find all migration files.
        """
        migrations = []

        for f in os.listdir(self._path):
            if f.endswith(".py") and not f.startswith("__init__."):
                mod_id = f[:-len(".py")]
                migrations.append(mod_id)
        return migrations

    def get_history(self):
        """ Get history of applied migrations """
        self.load_history()
        return map(lambda x: (x, self.history[x]), self.ordered_history)

    def get_migrations(self):
        """ Get migrations (ordered according to their dependencies). """
        if self.migrations is None:
            self.load_history()
            migration_ids = self.find_migrations()
            migrations = {}

            for mod_id in migration_ids:
                mod = self.load_migration(mod_id)
                mod.id = mod_id
                migrations[mod_id] = mod

            # List of unapplied migrations in topological order
            self.migrations = self.order_migrations(migrations, self.history)
        return self.migrations

    def order_migrations(self, migrations, history={}):
        """
        Order migrations according to their dependencies (topological sort using
        Kahn's algorithm - http://en.wikipedia.org/wiki/Topological_sorting).
        """
        graph_incoming = {} # nodes their incoming edges
        graph_outgoing = {} # nodes their outgoing edges

        # Create graph data structure
        for mod in migrations.values():
            # Remove all incoming edges from already applied migrations
            graph_incoming[mod.id] = filter(lambda x: x not in self.history, mod.depends_on)
            # Build graph_outgoing
            if mod.id not in graph_outgoing:
                graph_outgoing[mod.id] = []
            for edge in graph_incoming[mod.id]:
                if edge not in graph_outgoing:
                    graph_outgoing[edge] = []
                graph_outgoing[edge].append(mod.id)

        # Removed already applied migrations (assumes all dependencies prior to
        # this migration has been applied).
        for node_id in history.keys():
            start_nodes = [node_id, ]
            while start_nodes:
                node = start_nodes.pop()
                # Remove from direct dependents
                for d in graph_outgoing[node]:
                    graph_incoming[d] = filter(lambda x: x != node, graph_incoming[d])
                # Remove all prior dependencies
                if node in graph_incoming:
                    # Get dependencies, remove node, and recursively
                    # remove all dependencies.
                    depends_on = graph_incoming[node]

                    # Add dependencies to check
                    for d in depends_on:
                        graph_outgoing[d] = filter(lambda x: x != node, graph_outgoing[d])
                        start_nodes.append(d)

                    del graph_incoming[node]

        # Check for missing dependencies
        for node_id, depends_on in graph_incoming.items():
            for d in depends_on:
                if d not in graph_incoming:
                    raise Exception("Migration %s depends on an unknown migration %s" % (node_id, d))
                if migrations[node_id].repository != migrations[d].repository:
                    raise Exception("Migration %s depends on an migration from another repository %s" % (node_id, migrations[d].repository))

        # Nodes with no incoming edges
        start_nodes = filter(lambda x: len(graph_incoming[x]) == 0, graph_incoming.keys())
        topo_order = []

        while start_nodes:
            # Append node_n to list (it has no incoming edges)
            node_n = start_nodes.pop()
            topo_order.append(node_n)

            # For each node m with and edge from n to m
            for node_m in graph_outgoing[node_n]:
                # Remove the edge n to m
                graph_incoming[node_m] = filter(lambda x: x != node_n, graph_incoming[node_m])
                # If m has no incoming edges, add it to start_nodes.
                if not graph_incoming[node_m]:
                    start_nodes.append(node_m)

        for node, edges in graph_incoming.items():
            if edges:
                raise Exception("The migrations have at least one cyclic dependency involving %s." % node)

        return map(lambda x: migrations[x], topo_order)


class InvenioMigrator(Migrator):
    """
    Invenio migration engine

    Implements database operations for Invenio, as well as
    locations for migrations.
    """

    def __init__(self):
        # Path to load migrations from.
        super(InvenioMigrator, self).__init__(os.path.join(CFG_PREFIX, "lib/python/invenio/migrations/"), 'invenio.migrations')

    def load_history(self):
        """ Load migration history from database table """
        if not self.history:
            res = run_sql("SELECT migration, applied FROM migrations ORDER BY applied DESC, id DESC")

            for migration, applied in res:
                self.history[migration] = applied
                self.ordered_history.append(migration)

    def register_success(self, migration):
        """ Register a successful migration """
        run_sql("INSERT INTO migrations (repository, migration, applied) VALUES (%s,%s,NOW())", (migration.repository, migration.id, ))

#
# Invenio helper functions
#

def run_sql_ignore(query, *args, **kwargs):
    """ Execute SQL query but ignore any errors. """
    try:
        run_sql(query, *args, **kwargs)
    except Exception, e:
        print "WARNING: Failed to execute query %s: %s" % (query, unicode(e))
