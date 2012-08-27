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
Migration engine - Invenio specific parts (basically db access) have been 
factored out in the subclass InvenioMigrator.
"""

import os

from invenio.dbquery import run_sql
from invenio.config import CFG_PREFIX

class DbMigration(object):
    """
    Base class for all migrations
    """
    depends_on = []
    module = ''
    
    def get_doc(self):
        """ Get first line of documentation for migration class """
        try:
            return " (%s)" % self.__class__.__doc__.split("\n")[0].strip()
        except Exception:
            return ''

    def forward(self):
        pass


class Migrator(object):
    """
    Base class responsible for loading and executing migrations
    """
    def __init__(self, path, package):
        self._path = path
        self._package = package
        self.migrations = None
        self.history = {}
        self.ordered_history = []
    
    
    def apply(self, migration):
        """ Main function for applying a migration """
        migration.forward()
        self.register_success( migration )
    
    
    def register_success(self, migration):
        """ Register a successful migration (must be implemented by subclass) """
        raise NotImplementedError()
    
    
    def load_history(self):
        """ Load migration history from database table (must be implemented by subclass) """
        raise NotImplementedError()
    
    
    def load_migration(self, mod_id):
        """ Load python migration module """
        module = '%s.%s' % (self._package, mod_id)
        try:
            mod = __import__(module, globals(), locals(), ['Migration'])
            return mod.Migration()
        except ImportError:
            raise Exception("Cannot import migration %s" % module)
    
    
    def find_unapplied_migrations(self):
        """ Find all unapplied migration files. """
        self.load_history()
        
        migrations = []
        
        for f in os.listdir(self._path):
            if f.endswith(".py") and not f.startswith("__init__."):
                mod_id = f[:-len(".py")]
                if mod_id not in self.history: 
                    migrations.append(mod_id)
        return migrations
    
    
    def get_history(self):
        """ Get history of applied migrations """
        self.load_history()
        return map(lambda x: (x, self.history[x]), self.ordered_history)
    
    
    def get_migrations(self):
        """ Get migrations (ordered according to their dependencies). """
        if self.migrations is None:
            migration_ids = self.find_unapplied_migrations()
            migrations = {}
            
            for mod_id in migration_ids:
                mod = self.load_migration(mod_id)
                mod.id = mod_id
                migrations[mod_id] = mod
            
            # List of migrations in topological order
            self.migrations = self.order_migrations( migrations )
        return self.migrations
    
    
    def order_migrations(self, migrations):
        """ Order migrations according to their dependencies (topological sort) """
        graph_incoming = {} # nodes their incoming edges
        graph_outgoing = {} # nodes their outgoing edges
        
        # Create grap data structure
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
        
        # Check for missing dependencies
        for node_id, depends_on in graph_incoming.items():
            for d in depends_on:
                if d not in graph_incoming:
                    raise Exception("Migration %s depends on an unknown migration %s" % (node_id, d))
        
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
                graph_incoming[node_m] = filter( lambda x: x != node_n, graph_incoming[node_m])
                # If m has no incoming edges, add it to start_nodes.
                if not graph_incoming[node_m]:
                    start_nodes.append(node_m)
        
        for node, edges in graph_incoming.items():
            if edges:
                raise Exception("The migrations have at least one cyclic dependency involving %s." % node)
        
        return map(lambda x: migrations[x], topo_order)


class InvenioMigrator(Migrator):
    """ 
    Class for running migrations in Invenio.
    
    Implements database operations for Invenio.
    """
    def __init__(self):
        from invenio.config import CFG_PREFIX
        super(InvenioMigrator, self).__init__(os.path.join(CFG_PREFIX, "lib/python/invenio/migrations/"), 'invenio.migrations')
    
    def load_history(self):
        """ Load migration history from database table """
        if not self.history:
            res = run_sql("SELECT id, module, migration, applied FROM dbmigrations ORDER BY applied DESC, id DESC")
            
            for id, module, migration, applied in res:
                self.history[migration] = applied
                self.ordered_history.append(migration)
    
    def register_success(self, migration):
        """ Register a successful migration """
        res = run_sql("INSERT INTO dbmigrations (module, migration, applied) VALUES (%s,%s,NOW())", (migration.module, migration.id,))

# 
# Invenio helper functions
#

def run_sql_ignore(query, *args, **kwargs):
    """ Execute SQL query but ignore any errors. """
    try:
        run_sql(query, *args, **kwargs)
    except Exception, e:
        print "WARNING: Failed to execute query %s: %s" % (query, unicode(e))

def run_tabcreate():
    """ Run tabcreate.sql file to create new tables. """
    cmd = "%s/bin/dbexec < %s/lib/sql/invenio/tabcreate.sql" % (CFG_PREFIX,
        CFG_PREFIX)
    if os.system(cmd):
        print "ERROR: failed execution of", cmd
        sys.exit(1)
