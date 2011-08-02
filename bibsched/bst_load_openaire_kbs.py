#!/usr/bin/env python

from invenio.bibtask import write_message, task_update_progress, task_sleep_now_if_required
from invenio.dbquery import run_sql
from invenio.bibknowledge import add_kb_mapping, kb_exists, update_kb_mapping, add_kb, kb_mapping_exists, add_kb_mapping, remove_kb_mapping, get_kbr_keys, get_kb_mappings
from invenio.dnetutils import dnet_run_sql
from invenio.errorlib import register_exception

import datetime
import urllib
import sys
import gzip
if sys.hexversion < 0x2060000:
    try:
        import simplejson as json
    except ImportError:
        # Okay, no Ajax app will be possible, but continue anyway,
        # since this package is only recommended, not mandatory.
        pass
else:
    import json

CFG_ENTREZ = "ftp://ftp.ncbi.nih.gov/pubmed/J_Entrez.gz"

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        return json.JSONEncoder.default(self, obj)


def get_journals_from_entrez():
    global ENTREZ_JOURNALS
    try:
        return ENTREZ_JOURNALS
    except NameError:
        pass
    name, mimetype = urllib.urlretrieve(CFG_ENTREZ)
    ENTREZ_JOURNALS = {}
    item = {}
    for line in gzip.open(name):
        if line.startswith('---'):
            if item:
                ENTREZ_JOURNALS[item["JrId"]] = item
                item = {}
        else:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            item[key] = value
    if item:
        ENTREZ_JOURNALS[item["JrId"]] = item
    return ENTREZ_JOURNALS

#def _init_journals():
    #import gzip
    #run_sql(gzip.open("journals.sql.gz").read())

CFG_JOURNAL_KBS = {
    'journal_name': """tuple((item["JournalTitle"], "%s - %s" % (item["JournalTitle"], item["IsoAbbr"])) for item in get_journals_from_entrez().itervalues())"""
}

#CFG_JOURNAL_KBS = {
    #'journal_issn': 'SELECT name, issn FROM journals_journal',
    #'journal_essn': 'SELECT name, essn FROM journals_journal',
    #'journal_publisher': 'SELECT journals_journal.name, journals_publisher.name FROM journals_journal JOIN journals_publisher ON journals_journal.publisher_id=journals_publisher.id',
    #'journal_name': 'SELECT journals_journal.name, journals_variantname.name FROM journals_journal JOIN journals_variantname ON journals_journal.id=journals_variantname.journal_id'
#}

CFG_DNET_KBS = {
    #'project_acronym': 'SELECT grant_agreement_number, acronym FROM projects',
    #'project_title': 'SELECT grant_agreement_number, title FROM projects',
    #'json_projects': """SELECT grant_agreement_number,*
        #FROM projects
            #LEFT OUTER JOIN projects_projectsubjects ON project=projectid
            #LEFT OUTER JOIN projectsubjects ON project_subject=projectsubjectid
            #LEFT OUTER JOIN projects_contracttypes ON projects_contracttypes.project=projectid
            #LEFT OUTER JOIN contracttypes ON contracttype=contracttypeid
            #LEFT OUTER JOIN participants_projects ON participants_projects.project=projectid
            #LEFT OUTER JOIN participants ON beneficiaryid=participant
    #""",
    'json_projects': """SELECT projectid,grant_agreement_number,ec_project_website,acronym,call_identifier,end_date,start_date,title,fundedby FROM projects""",
    'projects': """SELECT grant_agreement_number, COALESCE(acronym, title) || ' - ' || COALESCE(title, acronym) || ' (' || grant_agreement_number || ')' FROM projects""",
    'project_subjects': "SELECT project, project_subject FROM projects_projectsubjects",
    'languages': "SELECT languageid, name FROM languages",
    'institutes': "SELECT legal_name, legal_name FROM organizations",
}

def none_run_sql(query):
    return eval(query)

def load_kbs(cfg, run_sql, in_task=False):
    for kb, query in cfg.iteritems():
        task_sleep_now_if_required(can_stop_too=True)
        if not kb_exists(kb):
            add_kb(kb)
        if in_task:
            write_message("Updating %s KB..." % kb)
        try:
            if not in_task:
                print "kb:", kb
                print "kb beginning:", len(get_kb_mappings(kb))
            if kb.startswith('json_'):
                encoder = ComplexEncoder()
                mapping, description = run_sql(query, with_desc=True)
                if not in_task:
                    print "mapping:", len(mapping)
                column_counter = {}
                new_description = []
                for column in description[1:]:
                    column = column[0]
                    counter = column_counter[column] = column_counter.get(column, 0) + 1
                    if counter > 1:
                        new_description.append('%s%d' % (column, counter))
                    else:
                        new_description.append(column)
                description = new_description
            else:
                mapping = run_sql(query)
                if not in_task:
                    print "mapping:", len(mapping)
                if kb == 'projects':
                    mapping = list(mapping)
                    mapping.append(('000000', 'NO PROJECT'))
                    mapping = tuple(mapping)
            original_keys = set([key[0] for key in get_kbr_keys(kb)])
            if not in_task:
                print "original_keys before:", len(original_keys)

            updated = 0
            added = 0
            for i, row in enumerate(mapping):
                key, value = row[0], row[1:]
                if kb.startswith('json_'):
                    value = encoder.encode(dict(zip(description, value)))
                else:
                    value = value[0]
                if value:
                    if key in original_keys:
                        original_keys.remove(key)
                    if in_task:
                        task_update_progress("%s - %s%%" % (kb, i * 100 / len(mapping)))
                    if kb_mapping_exists(kb, key):
                        updated += 1
                        update_kb_mapping(kb, key, key, value)
                    else:
                        added += 1
                        add_kb_mapping(kb, key, value)
            if not in_task:
                print "updated:", updated, "added:", added
                print "kb after update:", len(get_kb_mappings(kb))
                print "original_keys after:", len(original_keys)
            if in_task:
                task_update_progress("Cleaning %s" % kb)
            for key in original_keys:
                remove_kb_mapping(kb, key)
            if not in_task:
                print "kb after remove:", len(get_kb_mappings(kb))
        except:
            register_exception(alert_admin=True, prefix="Error when updating KB %s" % kb)
            continue


def bst_load_openaire_kbs(journals=True):
    load_kbs(CFG_DNET_KBS, dnet_run_sql, in_task=True)
    if journals:
        load_kbs(CFG_JOURNAL_KBS, none_run_sql, in_task=True)

if __name__ == '__main__':
    bst_load_OpenAIRE_kbs(journals=True)