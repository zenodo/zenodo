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
Deposit engine for OpenAIRE

Adding new fields
=================
Following steps are necessary to add a new field:

  * openaire_deposit_config.py: Add to CFG_METADATA_FIELDS
  * openaire_deposit_checks.py: Add _check_field method and update CFG in bottom.
  * openaire_deposit_templates.py: Add to tmpl_form, and perhaps add more methods
  * openaire_form.tpl: Add HTML input fields.
  * openaire_deposit_engine.py: Adapt get_record() to make use of new field data.
  * Default_HTML_detailed.bft: Ensure field is displayed on submitted records
  * bibedit/etc/field_<name>.xml: Add field template for BibEdit.

  ... tests ...

Adding new publication types
=============================
Following steps are necessary to add a new publication type:

  * Update metadata schema (Google Docs)
  * openaire_deposit_config.py: Add to CFG_OPENAIRE_PUBLICATION_TYPES
  * openaire_deposit_config.py: Add to CFG_OPENAIRE_CC0_PUBLICATION_TYPES if needed.
  * openaire_deposit_config.py: Add to CFG_METADATA_FIELDS_GROUPS if needed
  * openaire_deposit_engine.py: Modify OpenAIREPublication.get_record()
  * openaire_deposit_engine_tests.py: Add test, test_<type>()
  * openaire_deposit_fixtures.py: Add fixture FIXTURES and MARC_FIXTURES
  * openaire_deposit_webinterface_tests.py: Modify test_submission()
  * openaire_form.tpl: Add <div class="typebox_%(id)s typebox_%(id)s_publishedArticle"> with fields.
  * bibedit/etc/field_type_<name>.xml: Add field template for BibEdit for the new type.
"""

from base64 import encodestring
from cgi import escape
import copy
import datetime
import os
import stat
import re
import shutil
import sys
import tempfile
import time

if sys.hexversion < 0x2060000:
    try:
        import simplejson as json
    except ImportError:
        # Okay, no Ajax app will be possible, but continue anyway,
        # since this package is only recommended, not mandatory.
        pass
else:
    import json

from invenio import template
from invenio.bibdocfile import generic_path2bidocfile, download_external_url
from invenio.bibformat import format_record
from invenio.bibformat_elements.bfe_fulltext import sort_alphanumerically
from invenio.bibknowledge import get_kb_mapping, get_kbr_keys
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.bibtask import task_low_level_submission
from invenio.config import CFG_SITE_LANG, CFG_SITE_URL, CFG_SITE_NAME, \
    CFG_SITE_ADMIN_EMAIL, CFG_SITE_SECURE_URL, CFG_OPENAIRE_PORTAL_URL
from invenio.dbquery import run_sql
from invenio.errorlib import register_exception
from invenio.jsonutils import json_unicode_to_utf8
from invenio.mailutils import send_email
from invenio.messages import gettext_set_language
from invenio.openaire_deposit_checks import CFG_METADATA_FIELDS_CHECKS
from invenio.openaire_deposit_config import CFG_OPENAIRE_PROJECT_DESCRIPTION_KB, \
    CFG_OPENAIRE_PROJECT_INFORMATION_KB, CFG_OPENAIRE_DEPOSIT_PATH, \
    CFG_OPENAIRE_MANDATORY_PROJECTS, CFG_METADATA_FIELDS, CFG_PUBLICATION_STATES, \
    CFG_OPENAIRE_CURATORS, CFG_METADATA_FIELDS_GROUPS
from invenio.openaire_deposit_utils import wash_form, \
    simple_metadata2namespaced_metadata, namespaced_metadata2simple_metadata, \
    strip_publicationid
from invenio.search_engine import record_empty
from invenio.textutils import wash_for_xml
from invenio.urlutils import create_url
from invenio.webinterface_handler import wash_urlargd
from invenio.webpage import page as invenio_page
from invenio.shellutils import mymkdir
from invenio.websubmit_functions.Report_Number_Generation import create_reference
from invenio.webuser import session_param_set, session_param_get, \
    collect_user_info, get_email

# Globals
openaire_deposit_templates = template.load('openaire_deposit')
_ = lambda x: x
_RE_SPACES = re.compile(r'\s+')


def get_project_description(projectid):
    """
    Get title of an EU project from the knowledge base, using the project
    id as key.
    """
    info = get_kb_mapping(CFG_OPENAIRE_PROJECT_DESCRIPTION_KB, str(projectid))
    if info:
        return info['value']
    else:
        return ''


def get_project_information_from_projectid(projectid):
    """
    Get dictionary of EU project information.

    Example of dictionary::

        {
            "fundedby": "CIP-EIP",
            "end_date": "2012-08-31",
            "title": "Advanced Biotech Cluster platforms for Europe",
            "acronym": "ABCEUROPE",
            "call_identifier": "EuropeINNOVA-ENT-CIP-09-C-N01S00",
            "ec_project_website": null,
            "grant_agreement_number": "245628",
            "start_date": "2009-09-01"
        }
    """
    info = get_kb_mapping(CFG_OPENAIRE_PROJECT_INFORMATION_KB, str(projectid))
    if info:
        return json_unicode_to_utf8(json.loads(info['value']))
    else:
        return {}


def get_all_publications_for_project(uid, projectid, ln, style):
    """
    """
    ret = {}
    for publicationid in run_sql("SELECT publicationid FROM eupublication WHERE uid=%s AND projectid=%s", (uid, projectid)):
        try:
            ret[publicationid[0]] = OpenAIREPublication(
                uid, publicationid[0], ln, style)
        except ValueError:
            register_exception(alert_admin=True)
    return ret


def get_favourite_authorships_for_user(uid, publicationid, term='', limit=50):
    """
    """
    ret = set(run_sql("SELECT DISTINCT authorship FROM OpenAIREauthorships WHERE uid=%s AND authorship LIKE %s ORDER BY authorship LIMIT %s", (uid, '%%%s%%' % term, limit)))
    if len(ret) < limit:
        ret |= set(run_sql("SELECT DISTINCT authorship FROM OpenAIREauthorships NATURAL JOIN eupublication WHERE projectid IN (SELECT projectid FROM eupublication WHERE uid=%s AND publicationid=%s) AND authorship LIKE %s ORDER BY authorship LIMIT %s", (uid, publicationid, '%%%s%%' % term, limit)))
    if len(ret) < limit:
        ret |= set(run_sql("SELECT DISTINCT authorship FROM OpenAIREauthorships NATURAL JOIN eupublication WHERE authorship LIKE %s ORDER BY authorship LIMIT %s", ('%%%s%%' % term, limit)))
    ret = [row[0] for row in ret]
    ret.sort()
    return ret


def get_favourite_keywords_for_user(uid, publicationid, term='', limit=50):
    """
    """
    ret = set(run_sql("SELECT DISTINCT keyword FROM OpenAIREkeywords WHERE uid=%s AND keyword LIKE %s ORDER BY keyword LIMIT %s", (uid, '%%%s%%' % term, limit)))
    if len(ret) < limit:
        ret |= set(run_sql("SELECT DISTINCT keyword FROM OpenAIREkeywords NATURAL JOIN eupublication WHERE projectid IN (SELECT projectid FROM eupublication WHERE uid=%s AND publicationid=%s) AND keyword LIKE %s ORDER BY keyword LIMIT %s", (uid, publicationid, '%%%s%%' % term, limit)))
    if len(ret) < limit:
        ret |= set(run_sql("SELECT DISTINCT keyword FROM OpenAIREkeywords NATURAL JOIN eupublication WHERE keyword LIKE %s ORDER BY keyword LIMIT %s", ('%%%s%%' % term, limit)))
    ret = [row[0] for row in ret]
    ret.sort()
    return ret


def update_favourite_authorships_for_user(uid, publicationid, authorships):
    """
    """
    run_sql("DELETE FROM OpenAIREauthorships WHERE uid=%s AND publicationid=%s", (uid, publicationid))
    for authorship in authorships.splitlines():
        run_sql("INSERT INTO OpenAIREauthorships(uid, publicationid, authorship) VALUES(%s, %s, %s)", (uid, publicationid, authorship))


def update_favourite_keywords_for_user(uid, publicationid, keywords):
    """
    """
    run_sql("DELETE FROM OpenAIREkeywords WHERE uid=%s AND publicationid=%s",
            (uid, publicationid))
    for keyword in keywords.splitlines():
        run_sql("INSERT INTO OpenAIREkeywords(uid, publicationid, keyword) VALUES(%s, %s, %s)", (uid, publicationid, keyword))


def normalize_authorships(authorships):
    """
    """
    ret = []
    for authorship in authorships.splitlines():
        authorship = authorship.split(':', 1)
        if len(authorship) == 2:
            name, affiliation = authorship
            name = ', '.join(item.strip() for item in name.split(','))
            affiliation = affiliation.strip()
            authorship = '%s: %s' % (name, affiliation)
        else:
            authorship = authorship[0].strip()
        ret.append(authorship)
    return '\n'.join(ret)


def normalize_authorship(authorship):
    """
    Normalize an author line, according to the pattern: "<name>: <affiliation>"
    """
    authorship = authorship.split(':', 1)
    if len(authorship) == 2:
        name, affiliation = authorship
        name = ', '.join(item.strip() for item in name.split(','))
        affiliation = affiliation.strip()
        authorship = '%s: %s' % (name, affiliation)
    else:
        authorship = authorship[0].strip()
    return authorship


def normalize_acronym(acronym):
    """ Normalize an acronym """
    acronym = acronym.replace("-", "_")
    return _RE_SPACES.sub('_', acronym)


def normalize_doi(doi_str):
    """ Normalize a DOI, by stripping away a 'doi:'-prefix """
    if doi_str.lower().startswith('doi:'):
        doi_str = doi_str[len('doi:'):]
    doi_str.strip()
    return doi_str


def normalize_text(text):
    """ Normalize a single-line string, but removing double spaces. """
    return _RE_SPACES.sub(' ', text)


def normalize_multivalue_field(val, sort=False, func=normalize_text):
    """
    Normalize a multivalue field (e.g a text-box with a value per line. Each
    value will be normalized by the `func` and possible sorted if requested.
    """
    ret = []
    for text in val.splitlines():
        text = func(text)
        if text and text not in ret:
            ret.append(text)
    if sort:
        ret.sort()
    return '\n'.join(ret)


def get_openaire_style(req=None):
    """
    Return the chosen OpenAIRE style (either portal or invenio) by parsing
    query argument or reading this from the session of the user. Defaults to
    to "invenio".

    @param req: HTTP Request
    @return: str, Style name.
    """
    if req is not None:
        form = req.form
        argd = wash_urlargd(form, {'style': (str, '')})
        style = argd['style']
        if style in ('portal', 'invenio'):
            session_param_set(req, 'style', style)
        else:
            try:
                style = session_param_get(req, 'style')
            except KeyError:
                style = 'invenio'
                session_param_set(req, 'style', 'invenio')
    else:
        style = 'invenio'
    return style


def portal_page(title, body, navtrail="", description="", keywords="",
                metaheaderadd="", uid=None,
                cdspageheaderadd="", cdspageboxlefttopadd="",
                cdspageboxleftbottomadd="", cdspageboxrighttopadd="",
                cdspageboxrightbottomadd="", cdspagefooteradd="", lastupdated="",
                language=CFG_SITE_LANG, verbose=1, titleprologue="",
                titleepilogue="", secure_page_p=0, req=None, errors=[], warnings=[],
                navmenuid="admin", navtrail_append_title_p=1, of="",
                rssurl=CFG_SITE_URL + "/rss", show_title_p=True,
                body_css_classes=None, project_information=None):
    """
    Render template with Portal layout.

    See also invenio.webpage.page
    """
    if req is not None:
        user_info = collect_user_info(req)
        username = user_info.get('external_fullname', user_info['email'])
        invenio_logouturl = "%s/youraccount/robotlogout" % CFG_SITE_SECURE_URL
    else:
        username = 'Guest'
        invenio_logouturl = ''
    if not CFG_OPENAIRE_PORTAL_URL:
        portalurl = "http://www.openaire.eu"
    else:
        portalurl = CFG_OPENAIRE_PORTAL_URL
    return openaire_deposit_templates.tmpl_page(title=title, body=body, headers=metaheaderadd, username=username, portalurl=portalurl, return_value=encodestring(invenio_logouturl), ln=language, project_information=project_information)


def page(title, body, navtrail="", description="", keywords="",
         metaheaderadd="", uid=None,
         cdspageheaderadd="", cdspageboxlefttopadd="",
         cdspageboxleftbottomadd="", cdspageboxrighttopadd="",
         cdspageboxrightbottomadd="", cdspagefooteradd="", lastupdated="",
         language=CFG_SITE_LANG, verbose=1, titleprologue="",
         titleepilogue="", secure_page_p=0, req=None, errors=[], warnings=[], navmenuid="admin",
         navtrail_append_title_p=1, of="", rssurl=CFG_SITE_URL + "/rss", show_title_p=True,
         body_css_classes=None, project_information=None):
    """
    Render template with the correct style (Portal or Invenio)
    """
    style = get_openaire_style(req)
    argd = wash_urlargd(req.form, {})
    if not metaheaderadd:
        metaheaderadd = openaire_deposit_templates.tmpl_headers(argd['ln'])
    body = """<noscript>
            <strong>WARNING: You must enable Javascript in your browser (or you must whitelist this website in the Firefox NoScript plugin) in order to properly deposit a publication into the OpenAIRE Orphan Record Repository.</strong>
        </noscript>
        """ + body
    if style == 'portal':
        return portal_page(title, body, navtrail, description, keywords,
                           metaheaderadd, uid,
                           cdspageheaderadd, cdspageboxlefttopadd,
                           cdspageboxleftbottomadd, cdspageboxrighttopadd,
                           cdspageboxrightbottomadd, cdspagefooteradd, lastupdated,
                           language, verbose, titleprologue,
                           titleepilogue, secure_page_p, req, errors, warnings, navmenuid,
                           navtrail_append_title_p, of, rssurl, show_title_p,
                           body_css_classes, project_information=project_information)
    else:
        return invenio_page(title, body, navtrail, description, keywords,
                            metaheaderadd, uid,
                            cdspageheaderadd, cdspageboxlefttopadd,
                            cdspageboxleftbottomadd, cdspageboxrighttopadd,
                            cdspageboxrightbottomadd, cdspagefooteradd, lastupdated,
                            language, verbose, titleprologue,
                            titleepilogue, secure_page_p, req, errors, warnings, navmenuid,
                            navtrail_append_title_p, of, rssurl, show_title_p,
                            body_css_classes)


def update_publication_projects_mapping(uid, publicationid, new_projectids):
    """
    """
    old_projectids = run_sql("SELECT projectid WHERE uid=%s AND publicationid=%s", (uid, publicationid))
    old_projectids = set([row[0] for row in old_projectids])
    new_projectids = set(new_projectids)
    for projectid in new_projectids - old_projectids:
        run_sql("INSERT INTO eupublication(uid, publicationid, projectid) VALUES(%s, %s, %s)", (uid, publicationid, projectid))
    for projectid in old_projectids - new_projectids:
        run_sql("DELETE FROM eupublication WHERE uid=%s AND publicationid=%s AND projectid=%s", (uid, publicationid, projectid))


def get_project_acronym(projectid):
    """
    """
    if projectid == 0:
        return 'no project'
    if projectid < 0:
        return None
    project_information = get_project_information_from_projectid(projectid)
    if project_information.get('acronym', '').strip():
        return project_information['acronym'].strip()
    title = project_information.get('title', '').strip().decode('utf-8')
    if len(title) > 10:
        title = title[:10] + u'...'
    title = title.encode('utf-8')
    if not title:
        return 'no acronym'
    return title


def get_project_information(uid, projectid, deletable, linked, ln, style, global_projectid=None, publicationid=None):
    """
    """
    project_information = get_project_information_from_projectid(projectid)
    existing_publications = run_sql("SELECT count(*) FROM eupublication WHERE uid=%s AND projectid=%s", (uid, projectid))
    return openaire_deposit_templates.tmpl_project_information(global_projectid=global_projectid, projectid=projectid, ln=ln, existing_publications=existing_publications[0][0], deletable=deletable, linked=linked, publicationid=publicationid, style=style, **project_information)


class UploadError(Exception):
    """ Exception used to signal a file upload error. """
    pass


def upload_url(form, uid, projectid=0, field='FileURL'):
    if field not in form:
        raise UploadError(_("It seems like you forgot to select a file to upload. Please click back button to select a file."))
    afileurl = form[field]
    if not afileurl.startswith("https://dl.dropbox.com/"):
        raise UploadError(_("It seems like you forgot to select a file to upload. Please click back button to select a file."))
    try:
        uploaded_file = download_external_url(afileurl)
    except StandardError:
        raise UploadError(_("A problem occurred when trying to download the file from DropBox. Please click back button and try uploading the file without using DropBox."))

    publication = OpenAIREPublication(uid)
    publication.link_project(projectid)
    publication.add_a_fulltext(uploaded_file, os.path.basename(afileurl))


def upload_file(form, uid, projectid=0, publicationid=None, req_file=None, field='Filedata'):
    """
    """
    from werkzeug import secure_filename

    if req_file:
        filename = secure_filename(req_file.filename)
        name = None
    else:
        if field not in form:
            raise UploadError(_("It seems like you forgot to select a file to upload. Please click back button to select a file."))
        afile = form[field]
        if not afile.filename:
            raise UploadError(_("It seems like you forgot to select a file to upload. Please click back button to select a file."))
        name = afile.file.name
        filename = afile.filename

    publication = OpenAIREPublication(uid, publicationid=publicationid)
    publication.link_project(projectid)
    publication.add_a_fulltext(name, filename, req_file=req_file)


def get_all_projectsids():
    """
    Get all project IDs

    @return: the set of all the valid projects IDs
    @rtype: set of string
    """
    ret = set(int(project[0]) for project in get_kbr_keys("projects"))
    ret.add(0)  # Add the NO-PROJECT
    return ret


def get_exisiting_projectids_for_uid(uid):
    """
    """
    return sort_projectsid_by_acronym([row[0] for row in run_sql("SELECT DISTINCT projectid FROM eupublication WHERE uid=%s", (uid,))])


def get_exisiting_publications_for_uid(uid):
    """
    """
    pubs = run_sql("SELECT publicationid, id_bibrec FROM eupublication WHERE uid=%s", (uid,))
    ctx = {
        'unsubmitted': [],
        'submitted': [],
    }
    for pubid, bibrec in pubs:
        try:
            p = OpenAIREPublication(uid, publicationid=pubid)
            try:
                title = p.metadata['title']
            except KeyError:
                title = "Untitled"

            if bibrec:
                ctx['submitted'].append({'id': pubid, 'recid': bibrec, 'title': title, 'timestamp': time.localtime(p.metadata.get('__cd__', time.time()))})
            else:
                ctx['unsubmitted'].append({'id': pubid, 'recid': None,  'title': title, 'timestamp': time.localtime(p.metadata.get('__cd__', time.time()))})
        except ValueError:
            pass

        ctx['submitted'].sort(key=lambda x: x['timestamp'])
        ctx['unsubmitted'].sort(key=lambda x: x['timestamp'])

    return ctx
    #return sort_projectsid_by_acronym([row[0] for row in )])


def sort_projectsid_by_acronym(projectids):
    """
    """
    decorated_projectsid = [(get_project_description(
        projectid), projectid) for projectid in projectids]
    decorated_projectsid.sort()
    return [row[1] for row in decorated_projectsid]


def mymkdtemp(dir=None, prefix=''):
    path = tempfile.mkdtemp(dir=dir, prefix=prefix)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    return path

class OpenAIREPublication(object):
    """
    """

    def __init__(self, uid, publicationid=None, ln=CFG_SITE_LANG, style='invenio'):
        """
        """
        self.__deleted = False
        self._metadata = {}
        self._metadata['__uid__'] = uid
        self._metadata['__publicationid__'] = publicationid
        self.__ln = ln
        self.__style = style
        if publicationid is None:
            self.status = 'initialized'
            mymkdir(os.path.join(CFG_OPENAIRE_DEPOSIT_PATH, str(uid)))
            while True:
                self.path = mymkdtemp(dir=os.path.join(
                    CFG_OPENAIRE_DEPOSIT_PATH, str(uid),), prefix='')
                publicationid = self._metadata[
                    '__publicationid__'] = os.path.basename(self.path)
                if '_' not in self.publicationid:
                    ## We don't want '_' at all in publicationid!
                    break
                os.rmdir(self.path)
            self._metadata['__cd__'] = self._metadata['__md__'] = time.time()
            run_sql("INSERT IGNORE INTO eupublication(uid, publicationid, projectid) VALUES(%s, %s, 0)", (self.uid, publicationid))
            self.__touched = True
        else:
            self.__touched = False
            self.path = os.path.join(
                CFG_OPENAIRE_DEPOSIT_PATH, str(uid), str(publicationid))
            if not os.path.exists(self.path):
                raise ValueError("publicationid %s does not exist for user %s" % (publicationid, uid))
        self.fulltext_path = os.path.join(self.path, 'files')
        self.metadata_path = os.path.join(self.path, 'metadata')
        self.fulltexts = {}
        self.warnings = {}
        self.errors = {}
        self._initialize_storage()
        self._load()

    def __del__(self):
        """
        """
        if not self.__deleted and self.__touched:
            self._dump()

    def link_project(self, projectid):
        """
        """
        if projectid == 0:
            if not run_sql("SELECT * FROM eupublication WHERE uid=%s AND publicationid=%s", (self.uid, self.publicationid)):
                run_sql("INSERT IGNORE INTO eupublication(uid, publicationid, projectid) VALUES(%s, %s, 0)", (self.uid, self.publicationid))
        else:
            run_sql("INSERT IGNORE INTO eupublication(uid, publicationid, projectid) VALUES(%s, %s, %s)", (self.uid, self.publicationid, projectid))
            run_sql("DELETE FROM eupublication WHERE uid=%s AND publicationid=%s AND projectid=0", (self.uid, self.publicationid))
        self.touch()

    def unlink_project(self, projectid):
        """
        """
        run_sql("DELETE FROM eupublication WHERE uid=%s AND publicationid=%s AND projectid=%s", (self.uid, self.publicationid, projectid))
        if not run_sql("SELECT * FROM eupublication WHERE uid=%s AND publicationid=%s", (self.uid, self.publicationid)):
            run_sql("INSERT IGNORE INTO eupublication(uid, publicationid, projectid) VALUES(%s, %s, 0)", (self.uid, self.publicationid))
        self.touch()

    def delete(self):
        """
        """
        self.__deleted = True
        run_sql("DELETE FROM eupublication WHERE uid=%s AND publicationid=%s",
                (self.uid, self.publicationid))
        shutil.rmtree(self.path)

    def _initialize_storage(self):
        """
        """
        mymkdir(os.path.join(self.path, 'files'))

    def _load(self):
        """
        """
        self._load_metadata()
        self._load_fulltexts()

    def _load_metadata(self):
        """
        """
        try:
            self._metadata.update(
                json_unicode_to_utf8(json.load(open(self.metadata_path))))
        except:
            self._dump_metadata()
            self._load_metadata()

    def _load_fulltexts(self):
        """
        """
        for fulltextid in os.listdir(self.fulltext_path):
            if not fulltextid.startswith('.') and os.path.isdir(os.path.join(self.fulltext_path, fulltextid)):
                for filename in os.listdir(os.path.join(self.fulltext_path, fulltextid)):
                    if not filename.startswith('.'):
                        self.fulltexts[fulltextid] = generic_path2bidocfile(os.path.join(self.fulltext_path, fulltextid, filename))

    def add_a_fulltext(self, original_path, filename, req_file=None):
        """
        """
        the_directory = mymkdtemp(prefix='', dir=self.fulltext_path)
        fulltextid = os.path.basename(the_directory)
        final_path = os.path.join(the_directory, os.path.basename(filename))
        if req_file:
            req_file.save(final_path)
        else:
            shutil.copy2(original_path, final_path)
        # Set file permission
        os.chmod(final_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        self.fulltexts[fulltextid] = generic_path2bidocfile(final_path)
        return fulltextid

    def remove_a_fulltext(self, fulltextid):
        """
        """
        if fulltextid in self.fulltexts:
            fulltext = self.fulltexts[fulltextid]
            os.remove(fulltext.get_full_path())
            del self.fulltexts[fulltextid]
            self.touch()
            return True
        return False

    def save(self):
        if not self.__deleted and self.__touched:
            self._dump()

    def _dump(self):
        """
        """
        self._dump_metadata()

    def _dump_metadata(self):
        """
        """
        if os.path.exists(self.metadata_path):
            backup_fd, backup_name = tempfile.mkstemp(prefix='metadata-%s-' % time.strftime("%Y%m%d%H%M%S"), suffix='', dir=self.path)
            os.write(backup_fd, open(self.metadata_path).read())
            os.close(backup_fd)
        json.dump(self._metadata, open(self.metadata_path, 'w'), indent=4)

    def merge_form(self, form):
        """
        """
        if self.status in ('initialized', 'edited'):
            self._metadata['__form__'] = form
            touched = False
            for key, value in self._metadata['__form__'].items():
                if value is not None:
                    if isinstance(value, basestring):
                        self._metadata[key] = wash_for_xml(value)
                    else:
                        self._metadata[key] = value
                    touched = True
            if touched:
                if self.status == 'initialized':
                    self.status = 'edited'
                self.touch()

    def get_form_values(self):
        return self.metadata.get('__form__')

    def touch(self):
        """
        """
        self._metadata['__md__'] = time.time()
        self.__touched = True

    def get_metadata_status(self):
        """
        """
        if self.errors:
            return 'error'
        if self.warnings:
            return 'warning'
        for field in CFG_METADATA_FIELDS:
            if field in self._metadata and self._metadata[field]:
                ## There is at least one field filled. Since there are no
                ## warnings or errors, that means it's OK :-)
                return 'ok'
        return 'empty'

    def upload_record(self):
        """
        """
        marcxml_path = os.path.join(self.path, 'marcxml')
        open(marcxml_path, 'w').write(self.marcxml)
        #task_low_level_submission(
        #    'bibupload', 'openaire', '-r', marcxml_path, '-P5')
        #self.status = 'submitted'
        #self.send_emails()

    def send_emails(self):
        """
        """
        content = openaire_deposit_templates.tmpl_confirmation_email_body(title=self._metadata['title'], authors=self._metadata['authors'].splitlines(), url=self.url, report_numbers=self.report_numbers, ln=self.ln)
        # No email to user anymore
        #send_email(CFG_SITE_ADMIN_EMAIL, get_email(self.uid), _("Successful deposition of a publication into OpenAIRE"), content=content)
        bibedit_url = CFG_SITE_URL + \
            "/record/edit/#state=edit&recid=%s" % self.recid
        content = openaire_deposit_templates.tmpl_curators_email_body(title=self._metadata['title'], authors=self._metadata['authors'].splitlines(), url=self.url, bibedit_url=bibedit_url)
        send_email(CFG_SITE_ADMIN_EMAIL, ", ".join(CFG_OPENAIRE_CURATORS), "Upload in %s needs your curation" % CFG_SITE_NAME, content=content)

    def get_projects_information(self, global_projectid=None):
        """
        """
        associated_projects = []
        for projectid in self.projectids:
            if projectid == 0:
                continue
            associated_projects.append(get_project_information(self.uid, projectid, deletable=True, linked=False, ln=self.ln, style=self.style, global_projectid=global_projectid, publicationid=self.publicationid))
        return openaire_deposit_templates.tmpl_projects_box(publicationid=self.publicationid, associated_projects=associated_projects, ln=self.ln)

    def get_publication_information(self):
        """
        """
        return openaire_deposit_templates.tmpl_publication_information(publicationid=self.publicationid, title=self._metadata.get('title', ""), authors=self._metadata.get('authors', ""), abstract=self._metadata.get('abstract', ""), ln=self.ln)

    def get_fulltext_information(self):
        """
        """
        out = ""
        for fulltextid, fulltext in self.fulltexts.iteritems():
            out += openaire_deposit_templates.tmpl_fulltext_information(filename=fulltext.get_full_name(), publicationid=self.publicationid, download_url=create_url("%s/deposit/getfile" % CFG_SITE_URL, {'publicationid': self.publicationid, 'fileid': fulltextid}), md5=fulltext.checksum, mimetype=fulltext.mime, format=fulltext.format, size=fulltext.size, ln=self.ln)
        return out

    def get_publication_form(self, current_projectid):
        """
        """
        fulltext_information = self.get_fulltext_information()
        publication_information = self.get_publication_information()
        projects_information = self.get_projects_information()
        return openaire_deposit_templates.tmpl_form(publicationid=self.publicationid, projectid=current_projectid, projects_information=projects_information, publication_information=publication_information, fulltext_information=fulltext_information, form=self._metadata.get("__form__"), metadata_status=self.metadata_status, warnings=simple_metadata2namespaced_metadata(self.warnings, self.publicationid), errors=simple_metadata2namespaced_metadata(self.errors, self.publicationid), ln=self.ln)

    def get_publication_preview(self):
        """
        """
        body = format_record(
            recID=self.recid, xml_record=self.marcxml, ln=self.ln, of='hd')
        return openaire_deposit_templates.tmpl_publication_preview(body, self.recid, ln=self.ln)

    def check_projects(self, check_project=CFG_OPENAIRE_MANDATORY_PROJECTS):
        """
        """
        if CFG_OPENAIRE_MANDATORY_PROJECTS:
            if len(self.projectids) == 1 and self.projectids[0] == 0:
                self.errors['projects'] = _("You must specify at least one FP7 Project within which your publication was created.")
            else:
                self.errors['projects'] = ""
        else:
            if len(self.projectids) == 1 and self.projectids[0] == 0:
                self.warnings['projects'] = _("No FP7 Projects are associated with your publication. Was this intentional.")
            else:
                self.warnings['projects'] = ""

    def check_metadata(self):
        """
        """
        self.errors, self.warnings = self.static_check_metadata(
            self._metadata, ln=self.ln)

        if self._metadata.get('authors') and not self.errors.get('authors'):
            self._metadata['authors'] = normalize_multivalue_field(
                self._metadata['authors'], func=normalize_authorship)
            update_favourite_authorships_for_user(
                self.uid, self.publicationid, self._metadata['authors'])

        if self._metadata.get('supervisors') and not self.errors.get('supervisors'):
            self._metadata['supervisors'] = normalize_multivalue_field(
                self._metadata['supervisors'], func=normalize_authorship)
            update_favourite_authorships_for_user(
                self.uid, self.publicationid, self._metadata['supervisors'])

        if self._metadata.get('keywords') and not self.errors.get('keywords'):
            self._metadata['keywords'] = normalize_multivalue_field(
                self._metadata['keywords'], sort=True)
            update_favourite_keywords_for_user(
                self.uid, self.publicationid, self._metadata['keywords'])

        if self._metadata.get('related_publications', '') and not self.errors.get('related_publications', ''):
            self._metadata['related_publications'] = normalize_multivalue_field(self.metadata.get('related_publications', ''), func=normalize_doi)

        if self._metadata.get('related_datasets', '') and not self.errors.get('related_datasets', ''):
            self._metadata['related_datasets'] = normalize_multivalue_field(self.metadata.get('related_datasets', ''), func=normalize_doi)

        if self._metadata.get('extra_report_numbers', '') and not self.errors.get('extra_report_numbers', ''):
            self._metadata['extra_report_numbers'] = normalize_multivalue_field(self.metadata.get('extra_report_numbers', ''))

    def static_check_metadata(metadata, publicationid=None, check_only_field=None, ln=CFG_SITE_LANG):
        """
        Given a mapping in metadata.
        Check that all the required metadata are properly set.
        """
        _ = gettext_set_language(ln)

        if publicationid:
            metadata = namespaced_metadata2simple_metadata(
                metadata, publicationid)

        if check_only_field:
            ## Just one check, if it actually exist for the given field
            fieldname = strip_publicationid(check_only_field, publicationid)
            if fieldname in CFG_METADATA_FIELDS_CHECKS:
                checks = [CFG_METADATA_FIELDS_CHECKS[fieldname]]
                errors = {fieldname: []}
                warnings = {fieldname: []}
            else:
                checks = []
                errors = {}
                warnings = {}
        else:
            checks = CFG_METADATA_FIELDS_CHECKS.values()
            errors = dict((field, []) for field in CFG_METADATA_FIELDS_CHECKS)
            warnings = dict(
                (field, []) for field in CFG_METADATA_FIELDS_CHECKS)

        for check in checks:
            ret = check(metadata, ln, _)
            if ret:
                assert(ret[1] in ('error', 'warning'))
                assert(ret[0]) in CFG_METADATA_FIELDS
                if ret[1] == 'error':
                    if ret[0] not in errors:
                        errors[ret[0]] = ret[2]
                    else:
                        errors[ret[0]] += ret[2]
                elif ret[1] == 'warning':
                    if ret[0] not in warnings:
                        warnings[ret[0]] = ret[2]
                    else:
                        warnings[ret[0]] += ret[2]
        for errorid, error_lines in errors.items():
            errors[errorid] = '<br />'.join(error_lines)
        for warningid, warning_lines in warnings.items():
            warnings[warningid] = '<br />'.join(warning_lines)
        if publicationid:
            errors = simple_metadata2namespaced_metadata(errors, publicationid)
            warnings = simple_metadata2namespaced_metadata(
                warnings, publicationid)
        return errors, warnings
    static_check_metadata = staticmethod(static_check_metadata)

    def get_ln(self):
        """
        """
        return self.__ln

    def get_status(self):
        """
        """
        if self._metadata['__status__'] == 'submitted':
            ## The record has been submitted into Invenio. Let's poll to see if it's actually there:
            if not record_empty(self.recid):
                ## FIXME: change this to pendingapproval once
                ## approval workflow is implemented.
                self._metadata['__status__'] = 'approved'
        return self._metadata['__status__']

    def set_status(self, new_status):
        """
        """
        assert(new_status in CFG_PUBLICATION_STATES)
        self._metadata['__status__'] = new_status

    def get_md(self):
        """
        """
        return self._metadata['__md__']

    def get_cd(self):
        """
        """
        return self._metadata['__cd__']

    def get_uid(self):
        """
        """
        return self._metadata['__uid__']

    def get_projectids(self):
        """
        """
        projectids = run_sql("SELECT projectid FROM eupublication WHERE uid=%s AND publicationid=%s", (self.uid, self.publicationid))
        if not projectids:
            return [0]
        else:
            return sort_projectsid_by_acronym([row[0] for row in projectids])

    def get_publicationid(self):
        """
        """
        return self._metadata['__publicationid__']

    def get_recid(self):
        """
        Generate a record ID.
        """
        if '__recid__' not in self._metadata:
            self._metadata['__recid__'] = run_sql("INSERT INTO bibrec(creation_date, modification_date) values(NOW(), NOW())")
            self.touch()
        run_sql("UPDATE eupublication SET id_bibrec=%s WHERE uid=%s AND publicationid=%s", (self._metadata['__recid__'], self.uid, self.publicationid))
        return self._metadata['__recid__']

    def get_year(self):
        """
        Get year of publication date.
        """
        if self._metadata.get('publication_date'):
            return self._metadata['publication_date'][:4]
        else:
            return datetime.datetime.today().year

    def get_report_numbers(self):
        """
        """
        report_numbers = self._metadata.get('report_numbers', {})
        year = self.year
        for projectid in self.projectids:
            project_information = get_project_information_from_projectid(
                projectid)
            acronym = project_information.get('acronym', '')
            acronym = normalize_acronym(acronym)
            if acronym not in report_numbers:
                if acronym:
                    report_number = create_reference(os.path.join("OpenAIRE", acronym, "lastid_%s" % year), "OpenAIRE-%s-%s" % (acronym, year))
                else:
                    report_number = create_reference(os.path.join("OpenAIRE", "lastid_%s" % year), "OpenAIRE-GENERAL-%s" % year)
                report_numbers[acronym] = report_number
        self._metadata['report_numbers'] = report_numbers
        ret = report_numbers.values()
        ret = sort_alphanumerically(ret)
        return ret

    def get_style(self):
        """
        """
        return self.__style

    def get_url(self):
        """
        """
        return "%s/record/%s" % (CFG_SITE_URL, self.recid)

    def get_names(self, field):
        """
        Get authors as as a list of 2-tuples (name, affiliation).
        """
        names = []
        for author_str in [author.strip() for author in self._metadata[field].splitlines() if author.strip()]:
            if ':' in author_str:
                name, affil = author_str.split(':', 1)
                name = name.strip()
                affil = affil.strip()
            else:
                name = author_str.strip()
                affil = None
            names.append((name, affil))
        return names

    def get_authors(self):
        """
        Get authors as as a list of 2-tuples (name, affiliation).
        """
        return self.get_names('authors')

    def get_supervisors(self):
        """
        Get supervisors as as a list of 2-tuples (name, affiliation).
        """
        return self.get_names('supervisors')

    def get_related_dois(self, field):
        """
        Get list of DOIs for related field
        """
        pubs = []
        for doi_str in [doi.strip() for doi in self._metadata.get(field, '').splitlines() if doi.strip()]:
            doi = normalize_doi(doi_str)
            if doi:
                pubs.append(doi_str)
        return pubs

    def get_related_publications(self):
        return self.get_related_dois('related_publications')

    def get_related_datasets(self):
        return self.get_related_dois('related_datasets')

    def get_metadata(self):
        """
        Get a copy of the metadata.
        """
        return copy.deepcopy(self._metadata)

    # ===============================
    # Record generation
    # ===============================
    def get_marcxml(self):
        """
        Get MARCXML for this publication
        """
        return record_xml_output(self.get_record())

    def get_record(self):
        """
        Generate MARC record for publication

        This methods generated all common fields of the MARC record.
        Depending on the publication type, there might be several other fields.
        """
        rec = {}

        # Record ID
        record_add_field(rec, '001', controlfield_value=str(self.recid))

        # Report number
        report_numbers = self.report_numbers
        if report_numbers:
            record_add_field(rec, '037', subfields=[('a', report_numbers[0])])
            for report_number in report_numbers[1:]:
                record_add_field(rec, '088', subfields=[('a', report_number)])

        # Authors
        authors = self.authors
        for (i, (name, affil)) in enumerate(authors):
            if i == 0:
                field_no = '100'
            else:
                field_no = '700'
            subfields = [('a', name), ]
            if affil:
                subfields.append(('u', affil))
            record_add_field(rec, field_no, subfields=subfields)

        # Language
        record_add_field(
            rec, '041', subfields=[('a', self._metadata['language'])])

        # Title
        record_add_field(
            rec, '245', subfields=[('a', self._metadata['title'])])

        # Original title
        if self._metadata.get('original_title'):
            record_add_field(rec, '246', subfields=[('a',
                             self._metadata['original_title'])])

        # Abstract
        record_add_field(
            rec, '520', subfields=[('a', self._metadata['abstract'])])

        # Original abstract
        if self._metadata.get('original_abstract'):
            record_add_field(rec, '560', subfields=[('a',
                             self._metadata['original_abstract'])])

        # Notes
        if self._metadata.get('notes'):
            record_add_field(
                rec, '500', subfields=[('a', self._metadata['notes'])])

        # Keywords
        if self._metadata.get('keywords'):
            for keyword in self._metadata['keywords'].splitlines():
                keyword.strip()
                if keyword:
                    record_add_field(
                        rec, '653', ind1="1", subfields=[('a', keyword)])

        # Publication date
        if self._metadata.get('publication_date'):
            record_add_field(rec, '260', subfields=[('c',
                             self._metadata['publication_date'])])

        # ProjectID
        for projectid in self.projectids:
            if projectid:
                subfields = []
                project_description = get_project_description(projectid)
                if project_description:
                    subfields.append(('a', project_description))
                subfields.append(('c', str(projectid)))
                record_add_field(rec, '536', subfields=subfields)

        # Submitter
        user_info = collect_user_info(self.uid)
        if "email" in user_info:
            email = user_info["email"]
        else:
            email = get_email(self.uid)
        name = user_info.get(
            "external_fullname", user_info.get("nickname", "")).strip()
        record_add_field(
            rec, '856', ind1='0', subfields=[('f', email.encode('utf8')), ('y', name.encode('utf8'))])

        # DOI
        if self._metadata.get('doi'):
            doi = self._metadata['doi'].strip()
            if doi.lower().startswith('doi:'):
                doi = doi[len('doi:'):]
            if doi:
                record_add_field(
                    rec, '024', '7', subfields=[('a', doi), ('2', 'DOI')])

        # Collection
        record_add_field(rec, '980', subfields=[('a', 'PROVISIONAL')])

        # =========================
        # Publication type specific
        # =========================

        # Publication Type (defaults to publishedArticle, since old
        # submission before these changes wouldn't have a publication_type.
        pubtype = self._metadata.get('publication_type', 'publishedArticle')
        field_groups = CFG_METADATA_FIELDS_GROUPS[pubtype]

        if 'COLLECTION' in field_groups:
            record_add_field(rec, '980', subfields=[('b', pubtype.upper())])

        # Journal
        if 'JOURNAL' in field_groups:
            subfields = []
            if self._metadata.get('journal_title'):
                subfields.append(('p', self._metadata['journal_title']))
            if self._metadata.get('publication_date'):
                year = self._metadata['publication_date'][:4]
                subfields.append(('y', year))
            if self._metadata.get('issue'):
                subfields.append(('n', self._metadata['issue']))
            if self._metadata.get('volume'):
                subfields.append(('v', self._metadata['volume']))
            if self._metadata.get('pages'):
                subfields.append(('c', self._metadata['pages']))
            if subfields:
                record_add_field(rec, '909', 'C', '4', subfields=subfields)
            record_add_field(rec, '980', subfields=[('b', 'OPENAIRE')])

        # Access rights (open/closed access + embargo date
        if 'ACCESS_RIGHTS' in field_groups:
            # Access right
            record_add_field(rec, '542', subfields=[('l',
                             self._metadata['access_rights'])])

            # Embargo date
            if self._metadata.get('embargo_date'):
                record_add_field(rec, '942', subfields=[(
                    'a', self._metadata['embargo_date'])])

            # Firerole
            fft_status = ''
            if self._metadata['access_rights'] == 'embargoedAccess':
                fft_status = 'firerole: deny until "%s"\nallow any' % self._metadata['embargo_date']
            elif self._metadata['access_rights'] in ('closedAccess', 'restrictedAccess'):
                fft_status = 'status: %s' % self._metadata['access_rights']

            # Fulltext
            for key, fulltext in self.fulltexts.iteritems():
                subfields = [('a', fulltext.fullpath)]
                if fft_status:
                    subfields.append(('r', fft_status))
                record_add_field(rec, 'FFT', subfields=subfields)

        # CC0 and data set
        if 'CC0' in field_groups and not 'ACCESS_RIGHTS' in field_groups:
            # Access rights
            record_add_field(rec, '542', subfields=[('l', 'cc0')])

            # Data file (no access restriction required)
            for key, fulltext in self.fulltexts.items():
                subfields = [('a', fulltext.fullpath), ('d', 'Data')]
                record_add_field(rec, 'FFT', subfields=subfields)

        # THESIS
        if 'THESIS' in field_groups:
            # Supervisors
            supervisors = self.supervisors
            for (name, affil) in supervisors:
                subfields = [('a', name), ('4', 'ths')]
                if affil:
                    subfields.append(('u', affil))
                record_add_field(rec, '700', subfields=subfields)

            record_add_field(rec, '502', '', '', subfields=[
                                 ('c', self._metadata.get('university')),
                                 ('b', self._metadata.get('thesis_type'))])

            record_add_field(rec, '980', '', '', subfields=[
                ('b', self._metadata.get('thesis_type').upper()),
                ])

        # ISBN
        if 'ISBN' in field_groups:
            if self._metadata.get('isbn'):
                record_add_field(rec, '020', '', '', subfields=[
                                 ('a', self._metadata.get('isbn')), ])

        # Book
        if 'BOOKPART' in field_groups:
            subfields = [('t', self._metadata.get('book_title')), ('n', 'bookpart')]

            if self._metadata.get('book_pages'):
                subfields.append(('g', self._metadata.get('book_pages')))

            if self._metadata.get('publisher'):
                subfields.append(('b', self._metadata.get('publisher')))

            if self._metadata.get('place'):
                subfields.append(('a', self._metadata.get('place')))

            if self._metadata.get('isbn'):
                subfields.append(('z', self._metadata.get('isbn')))

            if self._metadata.get('publication_date'):
                year = self._metadata['publication_date'][:4]
                subfields.append(('c', year))

            record_add_field(rec, '773', '', '', subfields=subfields)

        if 'RELATED_PUBS' in field_groups:
            # Related publications
            for doi in self.related_publications:
                record_add_field(rec, '773', subfields=[('a', doi), ('n', 'pub')])

        # Related datasets
        if 'RELATED_DATA' in field_groups:
            for doi in self.related_datasets:
                record_add_field(rec, '773', subfields=[('a', doi), ('n', 'data')])

        # Dataset publisher
        if 'DATASET' in field_groups:
            dataset_publisher = self._metadata.get('dataset_publisher')
            if dataset_publisher:
                subfields = [('b', dataset_publisher)]

                if self._metadata.get('publication_date'):
                    year = self._metadata['publication_date'][:4]
                    subfields.append(('c', year))

                # Note publication date is record in 260__$c, from which the
                # publication year can be computed
                record_add_field(rec, '260', '', '', subfields=subfields)

        # Number of pages
        if 'PAGES_NO' in field_groups:
            # Number of pages
            if self._metadata.get('report_pages_no'):
                record_add_field(rec, '300', '', '', subfields=[(
                    'a', self._metadata.get('report_pages_no')), ])

        # Report numbers and report type
        if 'REPORT' in field_groups:
            # Report numbers
            if self._metadata.get('extra_report_numbers'):
                for report_num in self._metadata['extra_report_numbers'].splitlines():
                    report_num = report_num.strip()
                    if report_num:
                        record_add_field(
                            rec, '088', '', '', subfields=[('a', report_num)])

            # Report type
            if self._metadata.get('report_type'):
                record_add_field(rec, '980', '', '', subfields=[('b', "REPORT_%s" % self._metadata.get('report_type').upper()), ])

        # Imprint (place: publisher. year.)
        if 'IMPRINT' in field_groups:
            # Place and Publisher
            place = self._metadata.get('place', '')
            publisher = self._metadata.get('publisher', '')

            if place or publisher:
                subfields = []
                if place:
                    subfields.append(('a', self._metadata.get('place')))
                if publisher:
                    subfields.append(('b', self._metadata.get('publisher')))
                if self._metadata.get('publication_date'):
                    year = self._metadata['publication_date'][:4]
                    subfields.append(('c', year))
                # Note publication date is record in 260__$c, from which the
                # publication year can be computed
                record_add_field(rec, '260', '', '', subfields=subfields)

        # Meeting/conferences (type, title, acronym, dates, town, country, URL
        if 'MEETING' in field_groups:
            meeting_values = [
                ('a', self._metadata.get('meeting_title', '')),
                ('g', self._metadata.get('meeting_acronym', '')),
                ('d', self._metadata.get('meeting_dates', '')),
                ('c', self._metadata.get('meeting_town', '')),
                ('w', self._metadata.get('meeting_country', '')),
            ]

            subfields = []
            for code, val in meeting_values:
                if val:
                    subfields.append((code, val))
            record_add_field(rec, '711', '', '', subfields=subfields)

            meeting_url = self._metadata.get('meeting_url', '')
            if meeting_url:
                record_add_field(rec, '8564', '', '', subfields=[
                                    ('u', meeting_url), ('y', 'Meeting website')])

            # Contribution type (paper, poster, lecture, ...)
            contribution_type = self._metadata.get('contribution_type', '')
            if contribution_type:
                record_add_field(rec, '980', '', '', subfields=[('b', "MEETING_%s" % contribution_type.upper()), ])

        return rec

    # ==========
    # Properties
    # ==========
    ln = property(get_ln)
    status = property(get_status, set_status)
    md = property(get_md)
    cd = property(get_cd)
    uid = property(get_uid)
    projectids = property(get_projectids)
    publicationid = property(get_publicationid)
    recid = property(get_recid)
    metadata = property(get_metadata)
    metadata_status = property(get_metadata_status)
    marcxml = property(get_marcxml)
    url = property(get_url)
    year = property(get_year)
    report_numbers = property(get_report_numbers)
    authors = property(get_authors)
    supervisors = property(get_supervisors)
    related_publications = property(get_related_publications)
    related_datasets = property(get_related_datasets)
    style = property(get_style)
