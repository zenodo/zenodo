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

import urllib
import urllib2
import sys
if sys.hexversion < 0x2060000:
    try:
        import simplejson as json
    except ImportError:
        # Okay, no Ajax app will be possible, but continue anyway,
        # since this package is only recommended, not mandatory.
        pass
else:
    import json

from invenio.access_control_engine import acc_authorize_action
from invenio.bibknowledge import get_kbr_keys
from invenio.config import CFG_SITE_URL, CFG_SITE_SECURE_URL, CFG_OPENAIRE_PORTAL_URL
from invenio.messages import gettext_set_language
from invenio.openaire_deposit_engine import page, get_project_information, \
    OpenAIREPublication, wash_form, get_exisiting_projectids_for_uid, \
    get_all_projectsids, get_favourite_authorships_for_user, \
    get_all_publications_for_project, upload_file, get_openaire_style, \
    get_favourite_keywords_for_user, get_project_acronym
from invenio.openaire_deposit_utils import simple_metadata2namespaced_metadata
from invenio.session import get_session
from invenio.urlutils import create_url
from invenio.urlutils import redirect_to_url, make_canonical_urlargd
from invenio.webinterface_handler import wash_urlargd, WebInterfaceDirectory
from invenio.webinterface_handler_config import SERVER_RETURN, HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED
from invenio.webuser import collect_user_info, session_param_get, session_param_set
import invenio.template

openaire_deposit_templates = invenio.template.load('openaire_deposit')

class WebInterfaceOpenAIREDepositPages(WebInterfaceDirectory):
    _exports = [
        '', 'uploadifybackend', 'sandbox', 'checkmetadata',
        'ajaxgateway', 'checksinglefield', 'getfile',
        'authorships', 'keywords', 'portalproxy'
    ]

    def portalproxy(self, req, form):
        """
        """
        argd_query = wash_urlargd(form, {
            'option': (str, ''),
            'tmpl': (str, ''),
            'type': (str, ''),
            'ordering': (str, ''),
            'searchphrase': (str, ''),
            'Itemid': (int, 0)
        })
        argd_post = wash_urlargd(form, {
            'searchword': (str, '')
        })
        if argd_query['option'] == 'com_search' and argd_query['tmpl'] == 'raw' and argd_query['type'] == 'json' and argd_post['searchword']:
            proxy = urllib2.urlopen("%s/index.php?%s" % (CFG_OPENAIRE_PORTAL_URL, urllib.urlencode(argd_query)), urllib.urlencode(argd_post))
            content = proxy.read()
            content = json.loads(content)
            ## HACK to transform relative URLs into full URLs to the Portal
            if 'results' in content:
                for elem in content['results']:
                    if 'url' in elem and elem['url'].startswith('/'):
                        elem['url'] = CFG_OPENAIRE_PORTAL_URL + elem['url']
            return json.dumps(content)
        return ""

    def index(self, req, form):
        """
        Main submission page installed on /deposit (hack in Invenio source) with the 
        following features:
        
          * Two different themes/skins (for portal and for invenio)
          * Upload new file to start a publication submission.
          * Enter metadata for publication(s) related to a project
          
        URL parameters:
         * style: Theme/skin to use - "invenio" or "portal"
         * projectid: Work on publications for this project
         * delete: Delete file and publication
         * plus: ?
         * upload: Upload new file (without Uploadify backend)
        """
        argd = wash_urlargd(form, {
            'projectid': (int, -1),
            'delete': (str, ''),
            'publicationid': (str, ''),
            'plus': (int, -1),
            'linkproject': (int, -1),
            'unlinkproject': (int, -1),
            'style': (str, None),
            'upload': (str, '')})

        _ = gettext_set_language(argd['ln'])
        
        # Check if user is authorized to deposit publications 
        user_info = collect_user_info(req)
        auth_code, auth_message = acc_authorize_action(user_info, 'submit', doctype='OpenAIRE')
        if auth_code:
            if user_info['guest'] == '1':
                return redirect_to_url(req, "%s/youraccount/login%s" % (
                    CFG_SITE_SECURE_URL,
                        make_canonical_urlargd({
                    'referer' : "%s%s" % (
                        CFG_SITE_URL,
                        req.unparsed_uri),
                    "ln" : argd['ln']}, {})))
            else:
                return page(req=req, body=_("You are not authorized to use OpenAIRE deposition."), title=_("Authorization failure"), navmenuid="submit")

        # Get parameters
        projectid = argd['projectid']
        plus = argd['plus']
        style = get_openaire_style(req)
        
        if plus == -1:
            try:
                plus = bool(session_param_get(req, 'plus'))
            except KeyError:
                plus = False
                session_param_set(req, 'plus', plus)
        else:
            plus = bool(plus)
            session_param_set(req, 'plus', plus)

        # Check projectid
        all_project_ids = get_all_projectsids()

        if projectid not in all_project_ids:
            projectid = -1

        uid = user_info['uid']
        
        ## Perform file upload (if needed)
        if argd['upload']:
            
            if projectid < 0:
                projectid = 0
            upload_file(form, uid, projectid)

        if projectid < 0:
            selected_project = None
        else:
            selected_project = get_project_information(uid, projectid, deletable=False, linked=False, ln=argd['ln'], style=style)
        if projectid < 0:
            upload_to_projectid = 0
            upload_to_project_information = get_project_information(uid, 0, deletable=False, linked=False, ln=argd['ln'], style=style)
        else:
            upload_to_projectid = projectid
            upload_to_project_information = selected_project

        body = ""
        if projectid >= 0:
            ## There is a project on which we are working good!
            publications = get_all_publications_for_project(uid, projectid, ln=argd['ln'], style=style)
            if argd['publicationid'] in publications:
                if argd['addproject'] in all_project_ids:
                    publications[argd['publicationid']].link_project(argd['linkproject'])
                if argd['delproject'] in all_project_ids:
                    publications[argd['publicationid']].unlink_project(argd['unlinkproject'])
            if argd['delete'] and argd['delete'] in publications:
                ## there was a request to delete a publication
                publications[argd['delete']].delete()
                del publications[argd['delete']]

            forms = ""
            submitted_publications = ""
            for index, (publicationid, publication) in enumerate(publications.iteritems()):
                if req.method.upper() == 'POST':
                    publication.merge_form(form, ln=argd['ln'])
                if publication.status == 'edited':
                    publication.check_metadata()
                    publication.check_projects()
                    if 'submit_%s' % publicationid in form and not "".join(publication.errors.values()).strip():
                        ## i.e. if the button submit for the corresponding publication has been pressed...
                        publication.upload_record()
                if publication.status in ('initialized', 'edited'):
                    forms += publication.get_publication_form(projectid)
                else:
                    submitted_publications += publication.get_publication_preview()
            body += openaire_deposit_templates.tmpl_add_publication_data_and_submit(projectid, forms, submitted_publications, project_information=upload_to_project_information, ln=argd['ln'])
            body += openaire_deposit_templates.tmpl_upload_publications(projectid=upload_to_projectid, project_information=upload_to_project_information, session=get_session(req).sid(), style=style, ln=argd['ln'])
        else:
            body += openaire_deposit_templates.tmpl_upload_publications(projectid=upload_to_projectid, project_information=upload_to_project_information, session=get_session(req).sid(), style=style, ln=argd['ln'])
            projects = [get_project_information(uid, projectid_, deletable=False, ln=argd['ln'], style=style, linked=True) for projectid_ in get_exisiting_projectids_for_uid(user_info['uid']) if projectid_ != projectid]
            if projects:
                body += openaire_deposit_templates.tmpl_focus_on_project(existing_projects=projects, ln=argd['ln'])

        title = _('Orphan Repository')
        return page(body=body, title=title, req=req, project_information=get_project_acronym(projectid), navmenuid="submit")

    def uploadifybackend(self, req, form):
        """
        File upload via Uploadify (flash) backend.
        """
        argd = wash_urlargd(form, {'session': (str, ''), 'projectid': (int, -1)})
        _ = gettext_set_language(argd['ln'])
        session = argd['session']
        get_session(req=req, sid=session)
        user_info = collect_user_info(req)
        if user_info['guest'] == '1':
            raise ValueError(_("This session is invalid"))
        projectid = argd['projectid']
        if projectid < 0:
            projectid = 0
        uid = user_info['uid']
        upload_file(form, uid, projectid)
        return "1"

    def getfile(self, req, form):
        """
        Download file for a submission which is currently in progress.
        """
        argd = wash_urlargd(form, {'publicationid': (str, ''), 'fileid': (str, '')})
        uid = collect_user_info(req)['uid']
        publicationid = argd['publicationid']
        fileid = argd['fileid']
        publication = OpenAIREPublication(uid, publicationid, ln=argd['ln'])
        fulltext = publication.fulltexts[fileid]
        return fulltext.stream(req)

    def sandbox(self, req, form):
        """
        TOOD: Document
        """
        body = """
<div id="projects_%(publicationid)s">

</div>
"""
        return page(title='sandbox', body=body, req=req)

    def authorships(self, req, form):
        """
        Return list of authors used for auto-completion 
        in the authors field.
        
        Return response as JSON. 
        """
        argd = wash_urlargd(form, {'publicationid': (str, ''), 'term': (str, '')})
        user_info = collect_user_info(req)
        uid = user_info['uid']
        req.content_type = 'application/json'
        term = argd['term']
        publicationid = argd['publicationid']
        ret = get_favourite_authorships_for_user(uid, publicationid, term)
        if ret:
            return json.dumps(ret)
        if ':' in term:
            ## an institution is being typed
            name, institute = term.split(':', 1)
            institute = institute.strip()
            if len(institute) > 1:
                institutes = [row[0] for row in get_kbr_keys('institutes', searchkey=institute, searchtype='s')]
                institutes.sort()
                return json.dumps(["%s: %s" % (name, institute) for institute in institutes[:100]])
        return json.dumps([])

    def keywords(self, req, form):
        """
        Return list of keywords used for auto-completion 
        in keywords field.
        
        Return response as JSON. 
        """
        argd = wash_urlargd(form, {'publicationid': (str, ''), 'term': (str, '')})
        user_info = collect_user_info(req)
        uid = user_info['uid']
        req.content_type = 'application/json'
        term = argd['term']
        publicationid = argd['publicationid']
        ret = get_favourite_keywords_for_user(uid, publicationid, term)
        if ret:
            return json.dumps(ret)
        return json.dumps([])

    def ajaxgateway(self, req, form):
        """
        """
        argd = wash_urlargd(form, {'projectid': (str, ''), 'publicationid': (str, ''), 'action': (str, ''), 'current_field': (str, '')})
        
        # Get parameters
        action = argd['action']
        publicationid = argd['publicationid']
        projectid = argd['projectid']
        
        # Check if action is supported
        assert(action in ('save', 'verify_field', 'submit', 'unlinkproject', 'linkproject'))
        
        # JSON return dictionary
        out = {
            'errors': {},
            'warnings': {},
            'addclasses': {},
            'delclasses': {},
            'substitutions': {},
            'appends': {},
            'hiddens': [],
            'showns': [],
            'action' : action,
        }
        
        if action == 'verify_field':
            current_field = argd['current_field']
            assert(current_field)
            metadata = wash_form(form, publicationid)
            out["errors"], out["warnings"] = OpenAIREPublication.static_check_metadata(metadata, publicationid, check_only_field=current_field, ln=argd['ln'])
        else:
            user_info = collect_user_info(req)
            auth_code, auth_message = acc_authorize_action(user_info, 'submit', doctype='OpenAIRE')
            assert(auth_code == 0)
            uid = user_info['uid']
            publication = OpenAIREPublication(uid, publicationid, ln=argd['ln'])
            if action == 'unlinkproject':
                publication.unlink_project(projectid)
                out["substitutions"]["#projectsbox_%s" % publicationid] = publication.get_projects_information()
                publication.check_projects()
                out["errors"], out["warnings"] = simple_metadata2namespaced_metadata(publication.errors, publicationid), simple_metadata2namespaced_metadata(publication.warnings, publicationid)
            elif action == 'linkproject':
                publication.link_project(projectid)
                out["substitutions"]["#projectsbox_%s" % publicationid] = publication.get_projects_information()
                publication.check_projects()
                out["errors"], out["warnings"] = simple_metadata2namespaced_metadata(publication.errors, publicationid), simple_metadata2namespaced_metadata(publication.warnings, publicationid)
            else:
                publication.merge_form(form)
                publication.check_metadata()
                publication.check_projects()
                out["errors"], out["warnings"] = simple_metadata2namespaced_metadata(publication.errors, publicationid), simple_metadata2namespaced_metadata(publication.warnings, publicationid)
                if "".join(out["errors"].values()).strip(): #FIXME bad hack, we need a cleaner way to discover if there are errors
                    out['addclasses']['#status_%s' % publicationid] = 'error'
                    out['delclasses']['#status_%s' % publicationid] = 'warning ok empty'
                elif "".join(out["warnings"].values()).strip():
                    out['addclasses']['#status_%s' % publicationid] = 'warning'
                    out['delclasses']['#status_%s' % publicationid] = 'error ok empty'
                else:
                    out['addclasses']['#status_%s' % publicationid] = 'ok'
                    out['delclasses']['#status_%s' % publicationid] = 'warning error empty'

                if action == 'save':
                    out["substitutions"]['#publication_information_%s' % publicationid] = publication.get_publication_information()
                elif action == 'submit':
                    if not "".join(out["errors"].values()).strip():
                        publication.upload_record()
                        out["appends"]['#submitted_publications'] = publication.get_publication_preview()
                        out["showns"].append('#submitted_publications')
                        out["hiddens"].append('#header_row_%s' % publicationid)
                        out["hiddens"].append('#body_row_%s' % publicationid)
        req.content_type = 'application/json'
        return json.dumps(out)

    __call__ = index
