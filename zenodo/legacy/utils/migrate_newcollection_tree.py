# -*- coding: utf-8 -*-
#
## This file is part of Zenodo.
## Copyright (C) 2012, 2013 CERN.
##
## Zenodo is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Zenodo is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.


from invenio.websearchadminlib import add_col, add_col_dad_son, delete_col
from invenio.dbquery import run_sql

COLLECTION_TREE = {
    'name' : 'OpenAIRE Orphan Record Repository', 'query' : '',
    'children' : [
        {
            'name' : 'Articles & Reports',
            'query' : '',
            'children' : [
                { 'name' : 'Published Articles', 'query' : 'collection:"OPENAIRE"', 'children' : [] },
                { 'name' : 'Reports', 'query' : 'collection:"REPORTS"', 'children' : [] },
            ]
        },
        {
            'name' : 'Data sets', 'query' : 'collection:"DATA"',
            'children' : []
            #'children' : [
            #    { 'name' : 'Books', 'query' : 'collection:"BOOKS"', 'children' : [] },
            #    { 'name' : 'Reports', 'query' : 'collection:"REPORTS"', 'children' : [] },
            #]
        },
    ]
}


def add_children(parent_id,children):
    """
    Recursive function to add collection tree.
    """
    for child in reversed(children):
        # Add child
        ret, child_id = add_col(child['name'], child['query'])
        # Insert in tree
        add_col_dad_son(parent_id, child_id, 'r')
        # Add any children.
        add_children(child_id, child['children'])


def main():
    # Clean colleciton tree
    for (colID,) in run_sql("SELECT id FROM collection WHERE id>4"): # 4 is the last id in the old version
        delete_col(colID)

    # Remove query from root collection.
    res = run_sql("UPDATE collection SET dbquery=''  WHERE id=1")

    # Start with root and add
    add_children(1, COLLECTION_TREE['children'])


if __name__ == "__main__":
    main()