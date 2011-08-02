## This file is part of Invenio.
## Copyright (C) 2009, 2010, 2011 CERN.
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

"""Invenio BibKnowledge Administrator Interface."""

import MySQLdb
import os
import cgi
import sys

JSON_OK = False

if sys.hexversion < 0x2060000:
    try:
        import simplejson as json
        JSON_OK = True
    except ImportError:
        # Okay, no Ajax app will be possible, but continue anyway,
        # since this package is only recommended, not mandatory.
        JSON_OK = False
else:
    try:
        import json
        JSON_OK = True
    except ImportError:
        JSON_OK = False

from invenio import bibknowledge, bibknowledgeadminlib
from invenio.bibrankadminlib import check_user
from invenio.webpage import page, create_error_box
from invenio.webuser import getUid, page_not_authorized
from invenio.messages import wash_language, gettext_set_language
from invenio.urlutils import wash_url_argument, redirect_to_url
from invenio.config import CFG_SITE_LANG, CFG_SITE_URL, \
                           CFG_SITE_NAME, CFG_WEBDIR, CFG_OPENAIRE_SITE

__lastupdated__ = """$Date$"""

def index(req, ln=CFG_SITE_LANG, search="", descriptiontoo=""):
    """
    handle the bibknowledgeadmin.py/kb_manage call
    @param search search for a substring in kb names
    @param descriptiontoo .. and descriptions
    """
    return kb_manage(req, ln, search, descriptiontoo)

def kb_manage(req, ln=CFG_SITE_LANG, search="", descriptiontoo=""):

    """
    Main BibKnowledge administration page.

    @param ln language
    @param search search for a substring in kb names
    @param descriptiontoo .. and descriptions
    """
    ln = wash_language(ln)
    _ = gettext_set_language(ln)

    warnings = []
    # Check if user is authorized to administer
    # If not, still display page but offer to log in
    try:
        uid = getUid(req)
    except MySQLdb.Error:
        return error_page(req)
    (auth_code, auth_msg) = check_user(req, 'cfgbibknowledge')
    if not auth_code:
        is_admin = True
    else:
        is_admin = False

    navtrail = '''<a class="navtrail" href="%s/help/admin">%s</a>''' % \
               (CFG_SITE_URL, _("Admin Area"))
    if is_admin:
        return page(title=_("BibKnowledge Admin"),
                body=bibknowledgeadminlib.perform_request_knowledge_bases_management(ln=ln, search=search, descriptiontoo=descriptiontoo),
                language=ln,
                uid=uid,
                navtrail = navtrail,
                lastupdated=__lastupdated__,
                req=req,
                warnings=warnings)
    else:
        #redirect to login
        return page_not_authorized(req=req, text=auth_msg, navtrail=navtrail)


def kb_upload(req, kb, ln=CFG_SITE_LANG):
    """
    Uploads file rdffile.
    """
    ln = wash_language(ln)
    _ = gettext_set_language(ln)
    navtrail = '''<a class="navtrail" href="%s/kb?ln=%s">%s</a>''' % \
               (CFG_SITE_URL, ln, _("Knowledge Bases"))

    try:
        dummy = getUid(req)
    except MySQLdb.Error:
        return error_page(req)

    (auth_code, auth_msg) = check_user(req, 'cfgbibknowledge')
    if not auth_code:
        kb_id = wash_url_argument(kb, 'int')
        #get the form
        form = req.form
        #get the contents from the form
        if not form.has_key('file') or not form['file'].filename:
            return page(title=_("Cannot upload file"),
                        body = _("You have not selected a file to upload"),
                        language=ln,
                        navtrail = navtrail,
                        lastupdated=__lastupdated__,
                        req=req)
        fileitem = form['file']
        uploaddir = CFG_WEBDIR+"/kbfiles"

        #create a upload directory unless already exists
        if os.path.isfile(uploaddir):
            return page(title=_("Cannot upload file"),
                        body = "Cannot create directory " + \
                                uploaddir+" since it already" + \
                                " exists and it is a file",
                        language=ln,
                        navtrail = navtrail,
                        lastupdated=__lastupdated__,
                        req=req)
        if not os.path.isdir(uploaddir):
            try:
                os.mkdir(uploaddir)
            except:
                return page(title=_("Cannot upload file"),
                        body = "Cannot create directory "+uploaddir+ \
                               " maybe no access rights",
                        language=ln,
                        navtrail = navtrail,
                        lastupdated=__lastupdated__,
                        req=req)

        #if we are here we can try to write
        #get the name and the file..
        fn = str(kb_id)+".rdf"
        open(uploaddir+"/"+fn, 'w').write(fileitem.file.read())
        body = (_("File %s uploaded.") % ('kbfiles/' + cgi.escape(fn)))
        body += " <a href='"+CFG_SITE_URL+"/kb'>%s</a>" % _("Back")
        return(page(title=_("File uploaded"),
                    body = body,
                    language=ln,
                    navtrail = navtrail,
                    lastupdated=__lastupdated__,
                    req=req))
    else:
        return(page_not_authorized(req=req,
                                   text=auth_msg,
                                   navtrail=navtrail))

def kb_show(req, kb, sortby="to", ln=CFG_SITE_LANG, startat=0, search=""):
    """
    Shows the content of the given knowledge base id. Check for authentication and kb existence.
    Before displaying the content of the knowledge base, check if a form was submitted asking for
    adding, editing or removing a value.

    @param ln language
    @param kb the kb id to show
    @param sortby the sorting criteria ('from' or 'to')
    @param startat the number from which start showing mapping rules in kb
    @param search search for this string in the kb
    """

    ln = wash_language(ln)
    _ = gettext_set_language(ln)
    navtrail_previous_links = '''
         &gt; <a class="navtrail"
         href="%s/kb?ln=%s">%s</a>''' % (CFG_SITE_URL,
                                         ln, _("Manage Knowledge Bases"))

    try:
        uid = getUid(req)
    except MySQLdb.Error:
        return error_page(req)

    (auth_code, auth_msg) = check_user(req, 'cfgbibknowledge')
    if not auth_code:
        kb_id = wash_url_argument(kb, 'int')
        kb_name = bibknowledge.get_kb_name(kb_id)

        if kb_name is None:
            return page(title=_("Unknown Knowledge Base"),
                        body = "",
                        language=ln,
                        navtrail = navtrail_previous_links,
                        errors = [("ERR_KB_ID_UNKNOWN", kb)],
                        lastupdated=__lastupdated__,
                        req=req)
        return page(title=_("Knowledge Base %s" % kb_name),
                body=bibknowledgeadminlib.perform_request_knowledge_base_show(ln=ln,
                kb_id=kb_id, sortby=sortby, startat=startat,
                search_term=search),
                uid=uid,
                language=ln,
                navtrail = navtrail_previous_links,
                lastupdated=__lastupdated__,
                req=req)
    else:
        return page_not_authorized(req=req,
                                   text=auth_msg,
                                   navtrail=navtrail_previous_links)

def kb_show_attributes(req, kb, ln=CFG_SITE_LANG, sortby="to"):
    """
    Shows the attributes (name, description) of a given kb

    @param ln language
    @param kb the kb id to show
    @param sortby the sorting criteria ('from' or 'to')
    """
    ln = wash_language(ln)
    _ = gettext_set_language(ln)
    navtrail_previous_links = ''' &gt; <a class="navtrail" href="%s/kb?ln=%s">%s</a>''' % (CFG_SITE_URL, ln, _("Manage Knowledge Bases"))

    try:
        uid = getUid(req)
    except MySQLdb.Error:
        return error_page(req)

    (auth_code, auth_msg) = check_user(req, 'cfgbibknowledge')
    if not auth_code:

        kb_id = wash_url_argument(kb, 'int')
        kb_name = bibknowledge.get_kb_name(kb_id)

        if kb_name is None:
            return page(title=_("Unknown Knowledge Base"),
                        body = "",
                        language=ln,
                        navtrail = navtrail_previous_links,
                        errors = [("ERR_KB_ID_UNKNOWN", kb)],
                        lastupdated=__lastupdated__,
                        req=req)


        return page(title=_("Knowledge Base %s Attributes" % kb_name),
                body=bibknowledgeadminlib.perform_request_knowledge_base_show_attributes(ln=ln,
                                          kb_id=kb_id,
                                          sortby=sortby),
                uid=uid,
                language=ln,
                navtrail = navtrail_previous_links,
                lastupdated=__lastupdated__,
                req=req)
    else:
        return page_not_authorized(req=req, text=auth_msg,
                                   navtrail=navtrail_previous_links)

def kb_dynamic_update(req, kb_id, field, expression, collection,
                      ln=CFG_SITE_LANG):
    """
    Updates the configuration of a collection based KB by checking user
    rights and calling bibknowledgeadminlib..
    @param req request
    @param kb_id knowledge base id
    @param field configured field for this dynamic kb
    @param expression search expression
    @param collection search in this collection
    @param ln language
    """
    ln = wash_language(ln)
    _ = gettext_set_language(ln)
    navtrail_previous_links = ''' &gt; <a class="navtrail" href="%s/kb?ln=%s">%s</a>''' % (CFG_SITE_URL, ln, _("Manage Knowledge Bases"))

    try:
        dummy = getUid(req)
    except MySQLdb.Error:
        return error_page(req)
    (auth_code, auth_msg) = check_user(req, 'cfgbibknowledge')
    if not auth_code:
        #actual config call
        err = bibknowledgeadminlib.perform_update_kb_config(kb_id, field,
                                                            expression,
                                                            collection)
        if err:
            return page(title=_("Error"),
                        body = err,
                        language=ln,
                        navtrail = navtrail_previous_links,
                        lastupdated=__lastupdated__,
                        req=req)

        else:
            redirect_to_url(req, "kb?ln=%(ln)s&kb=%(kb_id)s" % {'ln':ln, 'kb_id': kb_id })
    else:
        return page_not_authorized(req=req,
                                   text=auth_msg,
                                   navtrail=navtrail_previous_links)

def kb_show_dependencies(req, kb, ln=CFG_SITE_LANG, sortby="to"):
    """
    Shows the dependencies of a given kb

    @param kb the kb id to show
    @param ln language
    @param sortby the sorting criteria ('from' or 'to')
    """
    ln = wash_language(ln)
    _ = gettext_set_language(ln)
    navtrail_previous_links = ''' &gt; <a class="navtrail" href="%s/kb?ln=%s">%s</a>''' % (CFG_SITE_URL, ln, _("Manage Knowledge Bases"))

    try:
        uid = getUid(req)
    except MySQLdb.Error:
        return error_page(req)

    (auth_code, auth_msg) = check_user(req, 'cfgbibknowledge')
    if not auth_code:
        kb_id = wash_url_argument(kb, 'int')
        kb_name = bibknowledge.get_kb_name(kb_id)

        if kb_name is None:
            return page(title=_("Unknown Knowledge Base"),
                        body = "",
                        language=ln,
                        navtrail = navtrail_previous_links,
                        errors = [("ERR_KB_ID_UNKNOWN", kb)],
                        lastupdated=__lastupdated__,
                        req=req)


        return page(title=_("Knowledge Base %s Dependencies" % kb_name),
                body=bibknowledgeadminlib.perform_request_knowledge_base_show_dependencies(ln=ln,
                                          kb_id=kb_id,
                                          sortby=sortby),
                uid=uid,
                language=ln,
                navtrail = navtrail_previous_links,
                lastupdated=__lastupdated__,
                req=req)
    else:
        return page_not_authorized(req=req,
                                   text=auth_msg,
                                   navtrail=navtrail_previous_links)

def kb_add_mapping(req, kb, mapFrom, mapTo, sortby="to", ln=CFG_SITE_LANG,
                   forcetype=None, replacements=None, kb_type=None):
    """
    Adds a new mapping to a kb.

    @param ln language
    @param kb the kb id to show
    @param sortby the sorting criteria ('from' or 'to')
    @param forcetype indicates if this function should ask about replacing left/right sides (None or 'no')
                     replace in current kb ('curr') or in all ('all')
    @param replacements an object containing kbname+++left+++right strings.
                     Can be a string or an array of strings
    @param kb_type None for normal from-to kb's, 't' for taxonomies
    """
    ln = wash_language(ln)
    _ = gettext_set_language(ln)

    navtrail_previous_links = ''' &gt; <a class="navtrail" href="%s/kb?ln=%s">%s</a>''' % (CFG_SITE_URL, ln, _("Manage Knowledge Bases"))

    try:
        dummy = getUid(req)
    except MySQLdb.Error:
        return error_page(req)

    (auth_code, auth_msg) = check_user(req, 'cfgbibknowledge')
    if not auth_code:

        kb_id = wash_url_argument(kb, 'int')
        kb_name = bibknowledge.get_kb_name(kb_id)

        if kb_name is None:
            return page(title=_("Unknown Knowledge Base"),
                        body = "",
                        language=ln,
                        navtrail = navtrail_previous_links,
                        errors = [("ERR_KB_ID_UNKNOWN", kb)],
                        lastupdated=__lastupdated__,
                        req=req)

        key = wash_url_argument(mapFrom, 'str')
        value = wash_url_argument(mapTo, 'str')

        #check if key or value already exists in some KB
        left_sides_match = bibknowledge.get_kb_mappings("", key, "")
        #check that the match is exact
        left_sides = []
        for m in left_sides_match:
            if m['key'] == key:
                left_sides.append(m)

        right_sides_match = bibknowledge.get_kb_mappings("", "", value)
        right_sides = []
        for m in right_sides_match:
            if m['value'] == value:
                right_sides.append(m)

        if (len(right_sides) == 0) and (len(left_sides) == 0):
            #no problems, just add in current
            forcetype = "curr"

        #likewise, if this is a taxonomy, just pass on
        if kb_type == 't':
            forcetype = "curr"

        if forcetype and not forcetype == "no":
            pass
        else:
            if len(left_sides) > 0:
                return page(title=_("Left side exists"),
                        body = bibknowledgeadminlib.perform_request_verify_rule(ln, kb_id, key, value, "left", kb_name, left_sides),
                        language=ln,
                        navtrail = navtrail_previous_links,
                        lastupdated=__lastupdated__,
                        req=req)

            if len(right_sides) > 0:
                return page(title=_("Right side exists"),
                        body = bibknowledgeadminlib.perform_request_verify_rule(ln, kb_id, key, value, "right", kb_name, right_sides),
                        language=ln,
                        navtrail = navtrail_previous_links,
                        lastupdated=__lastupdated__,
                        req=req)

        if forcetype == "curr":
            bibknowledge.add_kb_mapping(kb_name, key, value)
        if forcetype == "all":
            #a bit tricky.. remove the rules given in param replacement and add the current
            #rule in the same kb's
            if replacements:
                #"replacements" can be either a string or an array. Let's make it always an array
                if type(replacements) == type("this is a string"):
                    mystr = replacements
                    replacements = []
                    replacements.append(mystr)
                for r in replacements:
                    if r.find("++++") > 0:
                        (rkbname, rleft, dummy) = r.split('++++')
                        bibknowledge.remove_kb_mapping(rkbname, rleft)
                        #add only if this is not yet there..
                        if not bibknowledge.kb_mapping_exists(rkbname, key):
                            bibknowledge.add_kb_mapping(rkbname, key, value)

        redirect_to_url(req, "kb?ln=%(ln)s&kb=%(kb)s&sortby=%(sortby)s&kb_type=%(kb_type)s" % {'ln':ln,
                                                                                               'kb':kb_id,
                                                                                               'sortby':sortby,
                                                                                               'kb_type':kb_type})
    else:
        return page_not_authorized(req=req,
                                   text=auth_msg,
                                   navtrail=navtrail_previous_links)

def kb_edit_mapping(req, kb, key, mapFrom, mapTo,
                    update="", delete="", sortby="to", ln=CFG_SITE_LANG):
    """
    Edit a mapping to in kb. Edit can be "update old value" or "delete existing value"

    @param kb the knowledge base id to edit
    @param key the key of the mapping that will be modified
    @param mapFrom the new key of the mapping
    @param mapTo the new value of the mapping
    @param update contains a value if the mapping is to be updated
    @param delete contains a value if the mapping is to be deleted
    @param sortby the sorting criteria ('from' or 'to')
    """
    ln = wash_language(ln)
    _ = gettext_set_language(ln)
    navtrail_previous_links = ''' &gt; <a class="navtrail" href="%s/kb?ln=%s">%s</a>''' % (CFG_SITE_URL, ln, _("Manage Knowledge Bases"))

    try:
        dummy = getUid(req)
    except MySQLdb.Error:
        return error_page(req)

    (auth_code, auth_msg) = check_user(req, 'cfgbibknowledge')
    if not auth_code:
        kb_id = wash_url_argument(kb, 'int')
        kb_name = bibknowledge.get_kb_name(kb_id)

        if kb_name is None:
            return page(title=_("Unknown Knowledge Base"),
                        body = "",
                        language=ln,
                        navtrail = navtrail_previous_links,
                        errors = [("ERR_KB_ID_UNKNOWN", kb)],
                        lastupdated=__lastupdated__,
                        req=req)


        key = wash_url_argument(key, 'str')
        if delete != "":
            #Delete
            bibknowledge.remove_kb_mapping(kb_name, key)
        if update != "":
            #Update
            new_key = wash_url_argument(mapFrom, 'str')
            new_value = wash_url_argument(mapTo, 'str')
            bibknowledge.update_kb_mapping(kb_name, key, new_key, new_value)

        redirect_to_url(req, "kb?ln=%(ln)s&kb=%(kb)s&sortby=%(sortby)s" % {'ln':ln, 'kb':kb_id, 'sortby':sortby})
    else:
        return page_not_authorized(req=req,
                                   text=auth_msg,
                                   navtrail=navtrail_previous_links)

def uniq(alist):
    """a simple uniquer, return unique members of the list"""
    myset = {}
    return [myset.setdefault(e, e) for e in alist if e not in myset]

def kb_update_attributes(req, kb="", name="", description="", sortby="to",
                         ln=CFG_SITE_LANG, chosen_option=None, kb_type=None):
    """
    Update the attributes of the kb

    @param ln language
    @param kb the kb id to update
    @param sortby the sorting criteria ('from' or 'to')
    @param name the new name of the kn
    @param description the new description of the kb
    @param chosen_option set to dialog box value
    """

    ln = wash_language(ln)
    _ = gettext_set_language(ln)

    navtrail_previous_links = ''' &gt; <a class="navtrail" href="%s/kb?ln=%s">%s</a>''' % (CFG_SITE_URL, ln, _("Manage Knowledge Bases"))

    try:
        dummy = getUid(req)
    except MySQLdb.Error:
        return error_page(req)

    (auth_code, auth_msg) = check_user(req, 'cfgbibknowledge')
    if not auth_code:
        kb_id = wash_url_argument(kb, 'int')
        if chosen_option is not None:
            # Update could not be performed.
            # Redirect to kb attributes page
            redirect_to_url(req, "kb?ln=%(ln)s&amp;action=attributes&amp;kb=%(kb)s&sortby=%(sortby)s&kb_type=%(kb_type)s" % {'ln':ln, 'kb':kb_id, 'sortby':sortby, 'kb_type':kb_type})


        kb_name = bibknowledge.get_kb_name(kb_id)

        if kb_name is None:
            return page(title=_("Unknown Knowledge Base"),
                        body = "",
                        language=ln,
                        navtrail = navtrail_previous_links,
                        errors = [("ERR_KB_ID_UNKNOWN", kb)],
                        lastupdated=__lastupdated__,
                        req=req)

        new_name = wash_url_argument(name, 'str')
        if kb_name != new_name and bibknowledge.kb_exists(new_name):
            #A knowledge base with that name already exist
            #Do not update
            return dialog_box(req=req,
                              ln=ln,
                              title="Name already in use",
                              message="""<i>%s</i> cannot be renamed to %s:
                                        Another knowledge base already has that name.
                                        <br/>Please choose another name.""" % (kb_name,
                                                                             new_name),
                              navtrail=navtrail_previous_links,
                              options=[ _("Ok")])

        new_desc = wash_url_argument(description, 'str')
        bibknowledge.update_kb_attributes(kb_name, new_name, new_desc)
        redirect_to_url(req, "kb?ln=%(ln)s&kb=%(kb)s&sortby=%(sortby)s" % {'ln':ln, 'kb':kb_id, 'sortby':sortby})
    else:
        return page_not_authorized(req=req,
                                   text=auth_msg,
                                   navtrail=navtrail_previous_links)

def kb_export(req, kbname="", format="kbr", searchkey="", searchvalue="", searchtype="s", limit=None, ln=CFG_SITE_LANG):
    """
    Exports the given kb so that it is listed in stdout (the browser).

    @param req the request
    @param kbname knowledge base name
    @param expression evaluate this for the returned lines
    @param format 'kba' for authority file, 'kbr' for leftside-rightside, json
                  for json-formatted dictionaries
    @param searchkey include only lines that match this on the left side
    @param searchvalue include only lines that match this on the right side
    @param searchtype s = substring match, e = exact match
    @param limit how many results to return. None means all
    @param ln language
    """
    ln = wash_language(ln)
    _ = gettext_set_language(ln)
    navtrail_previous_links = ''' &gt; <a class="navtrail" href="%s/kb?ln=%s">%s</a>''' % (CFG_SITE_URL, ln, _("Manage Knowledge Bases"))
    if not kbname:
        return page(title=_("Knowledge base name missing"),
                    body = """Required parameter kbname
                              is missing.""",
                    language=ln,
                    navtrail = navtrail_previous_links,
                    lastupdated=__lastupdated__,
                    req=req)

    #in order to make 'wget' downloads easy we do not require authorization

    #first check the type of the KB
    kbtype = None
    kbinfo = None
    kbid = None
    kbinfos = bibknowledge.get_kbs_info("", kbname)
    if kbinfos:
        kbinfo = kbinfos[0]
        kbtype = kbinfo['kbtype']
        kbid = kbinfo['id']
    else:
        return page(title=_("Unknown knowledge base"),
                    body = _("There is no knowledge base with that name."),
                    language=ln,
                    navtrail = navtrail_previous_links,
                    lastupdated=__lastupdated__,
                    req=req)

    if kbtype == None or kbtype == 'w':
        # left side / right side KB
        mappings = bibknowledge.get_kb_mappings(kbname, searchkey, \
                                                searchvalue, searchtype)
        if CFG_OPENAIRE_SITE and JSON_OK:
            if format == 'jquery':
                ret = []
                for m in mappings:
                    label = m['value'] or m['key']
                    value = m['key'] or m['value']
                    ret.append({'label': label, 'value': value})
                if limit:
                    ret = ret[:limit]
                req.content_type = 'application/json'
                return json.dumps(ret)
            if format == 'jquery2':
                ret = []
                for m in mappings:
                    data = {'value': m['key']}
                    data.update(json.loads(m['value']))
                    ret.append(data)
                if limit:
                    ret = ret[:limit]
                req.content_type = 'application/json'
                return json.dumps(ret)
        if format and format[0] == 'j':
            # as JSON formatted string
            req.content_type = 'application/json'
            return bibknowledge.get_kb_mappings_json(kbname, searchkey, \
                                                    searchvalue, searchtype, limit)

        elif format == 'right' or format == 'kba':
            # as authority sequence
            seq = [m['value'] for m in mappings]
            seq = uniq(sorted(seq))
            for s in seq:
                req.write(s+"\n");
            return

        else:
            # as regularly formatted left-right mapping
            for m in mappings:
                req.write(m['key'] + '---' + m['value'] + '\n')
            return

    elif kbtype == 'd':
        # dynamic kb, another interface for perform_request_search
        if format and format[0] == 'j':
            req.content_type = "application/json"
            return bibknowledge.get_kbd_values_json(kbname, searchvalue)

        else:
            # print it as a list of values
            for hit in bibknowledge.get_kbd_values(kbname, searchvalue):
                req.write(hit + '\n')
            req.write('\n')
            return

    elif kbtype == 't': #taxonomy: output the file
        kbfilename = CFG_WEBDIR+"/kbfiles/"+str(kbid)+".rdf"
        try:
            f = open(kbfilename, 'r')
            for line in f:
                req.write(line)
            f.close()
        except:
            req.write("Reading the file "+kbfilename+" failed.")

    else:
        # This situation should never happen
        raise ValueError, "Unsupported KB Type: %s" % kbtype


def kb_add(req, ln=CFG_SITE_LANG, sortby="to", kbtype=""):
    """
    Adds a new kb
    @param req the request
    @param ln language
    @param sortby to or from
    @param kbtype type of knowledge base. one of: "", taxonomy, dynamic
    """
    ln = wash_language(ln)
    _ = gettext_set_language(ln)

    navtrail_previous_links = ''' &gt; <a class="navtrail" href="%s/kb?ln=%s">%s</a>''' % (CFG_SITE_URL, ln, _("Manage Knowledge Bases"))

    try:
        dummy = getUid(req)
    except MySQLdb.Error:
        return error_page(req)

    (auth_code, auth_msg) = check_user(req, 'cfgbibknowledge')
    if not auth_code:
        name = "Untitled"
        if kbtype == "taxonomy":
            name = "Untitled Taxonomy"
        if kbtype == "dynamic":
            name = "Untitled dynamic"
        kb_id = bibknowledge.add_kb(kb_name=name, kb_type=kbtype)
        redirect_to_url(req, "kb?ln=%(ln)s&amp;action=attributes&amp;kb=%(kb)s" % {'ln':ln, 'kb':kb_id, 'sortby':sortby})
    else:
        navtrail_previous_links = ''' &gt; <a class="navtrail" href="%s/kb?ln=%s">%s</a>''' % (CFG_SITE_URL, ln, _("Manage Knowledge Bases"))

        return page_not_authorized(req=req,
                                   text=auth_msg,
                                   navtrail=navtrail_previous_links)


def kb_delete(req, kb, ln=CFG_SITE_LANG, chosen_option=""):
    """
    Deletes an existing kb

    @param kb the kb id to delete
    """
    ln = wash_language(ln)
    _ = gettext_set_language(ln)
    navtrail_previous_links = ''' &gt; <a class="navtrail" href="%s/kb?ln=%s">%s</a> &gt; %s''' % (CFG_SITE_URL, ln, _("Manage Knowledge Bases"), _("Delete Knowledge Base"))

    try:
        dummy = getUid(req)
    except MySQLdb.Error:
        return error_page(req)

    (auth_code, auth_msg) = check_user(req, 'cfgbibknowledge')
    if not auth_code:
        kb_id = wash_url_argument(kb, 'int')
        kb_name = bibknowledge.get_kb_name(kb_id)
        if kb_name is None:
            return page(title=_("Unknown Knowledge Base"),
                        body = "",
                        language=ln,
                        navtrail = navtrail_previous_links,
                        errors = [("ERR_KB_ID_UNKNOWN", kb)],
                        lastupdated=__lastupdated__,
                        req=req)

        #Ask confirmation to user if not already done
        chosen_option = wash_url_argument(chosen_option, 'str')
        if chosen_option == "":
            return dialog_box(req=req,
                              ln=ln,
                              title="Delete %s" % kb_name,
                              message="""Are you sure you want to
                              delete knowledge base <i>%s</i>?""" % kb_name,
                              navtrail=navtrail_previous_links,
                              options=[_("Cancel"), _("Delete")])

        elif chosen_option==_("Delete"):
            bibknowledge.delete_kb(kb_name)

        redirect_to_url(req, "kb?ln=%(ln)s" % {'ln':ln})
    else:
        navtrail_previous_links = ''' &gt; <a class="navtrail" href="%s/kb">%s</a>''' % (CFG_SITE_URL, _("Manage Knowledge Bases"))

        return page_not_authorized(req=req, text=auth_msg,
                                   navtrail=navtrail_previous_links)


def dialog_box(req, url="", ln=CFG_SITE_LANG, navtrail="",
               title="", message="", options=None):
    """
    Returns a dialog box with a given title, message and options.
    Used for asking confirmation on actions.

    The page that will receive the result must take 'chosen_option' as parameter.

    @param url the url used to submit the options chosen by the user
    @param options the list of labels for the buttons given as choice to user
    """
    import invenio
    bibformat_templates = invenio.template.load('bibformat')

    if not options:
        options = []
    return page(title="",
                body = bibformat_templates.tmpl_admin_dialog_box(url,
                                                                 ln,
                                                                 title,
                                                                 message,
                                                                 options),
                language=ln,
                lastupdated=__lastupdated__,
                navtrail=navtrail,
                req=req)

def error_page(req):
    """
    Returns a default error page
    """
    return page(title="Internal Error",
                body = create_error_box(req, ln=CFG_SITE_LANG),
                description="%s - Internal Error" % CFG_SITE_NAME,
                keywords="%s, Internal Error" % CFG_SITE_NAME,
                language=CFG_SITE_LANG)
