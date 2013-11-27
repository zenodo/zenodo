#!/usr/bin/env python
## This file is part of Invenio.
## Copyright (C) 2010, 2011, 2012 CERN.
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
Tasklets to update the list of OpenAIRE keywords to match any edits
made in the records. 
"""

from invenio.bibtask import write_message, task_update_progress, task_sleep_now_if_required
from invenio.openaire_deposit_engine import OpenAIREPublication, normalize_multivalue_field
from invenio.intbitset import intbitset
from invenio.dbquery import run_sql

def add_missing_keywords( uid, publicationid, missing_keywords ):
    if uid and publicationid and missing_keywords:
        for keyword in missing_keywords.keys():
            write_message("Inserting missing keyword '%s'" % keyword) 
            run_sql("INSERT INTO OpenAIREkeywords(uid, publicationid, keyword) VALUES (%s, %s, %s)", (uid, publicationid, keyword))


def bst_openaire_keywords():
    """
    Tasklet to update the list of keywords and flag potential 
    keywords which should be split. 
    """
    current_uid = None
    current_pubid = None
    current_keywords = {} 
    
    # Iterate over all keywords (order by publication id) 
    res = run_sql("SELECT k.keyword, p.publicationid, p.uid, p.id_bibrec FROM eupublication AS p JOIN OpenAIREkeywords AS k ON p.publicationid=k.publicationid ORDER BY p.publicationid")
    total = len(res)
    i = 0
    
    # Any last minute regrets to stop?
    task_sleep_now_if_required(can_stop_too=True)
    write_message("Updating OpenAIREkeywords table (%s entries)..." %  total)
    
    for keyword, pubid, uid, recid in res:
        i += 1
        task_update_progress("%s - %s%%" % (total, i * 100 / total))
        
        # Check if we reached a new publication
        if current_pubid != pubid:
            # Add keywords which was not currently not there.
            add_missing_keywords(current_uid, current_pubid, current_keywords)
            
            # Stop task if required (we just reached a new publication, so we can
            # stop now in a consistent state.
            task_sleep_now_if_required(can_stop_too=True)
            
            # Reset state (i.e new record encountered)
            current_uid = uid
            current_pubid = pubid
            current_keywords = {}
            
            # Get current keywords for publication (either from record if exists,
            # otherwise from submitted form. 
            if recid:
                current_keywords = dict([(x[0],1) for x in run_sql("SELECT value FROM bibrec_bib65x JOIN bib65x ON id=id_bibxxx WHERE id_bibrec=%s AND tag='6531_a' ORDER BY id_bibrec, field_number", (recid,))])
            else:
                pub = OpenAIREPublication(uid, publicationid=pubid)
                current_keywords = dict([(x,1) for x in normalize_multivalue_field(pub._metadata.get('keywords',''), sort=True).splitlines()])
        
        # Check if keyword is in the current list of keywords.
        if keyword not in current_keywords:
            # If not, remove it.
            write_message("Removing keyword '%s'" % keyword)
            res = run_sql("DELETE FROM OpenAIREkeywords WHERE keyword=%s AND publicationid=%s", (keyword, pubid))
        else:
            del current_keywords[keyword] # Remove from dictionary, so we know if all keywords

    add_missing_keywords(current_uid, current_pubid, current_keywords)


if __name__ == '__main__':
    bst_openaire_keywords()
