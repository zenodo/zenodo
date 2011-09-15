# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2010, 2011 CERN.
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

import os
import re
from cgi import escape as cgi_escape

from invenio.config import CFG_SITE_LANG, CFG_SITE_URL, CFG_ETCDIR, CFG_VERSION
from invenio.messages import gettext_set_language
from invenio.textutils import nice_size

CFG_OPENAIRE_PAGE_TEMPLATE = open(os.path.join(CFG_ETCDIR, 'openaire_page.tpl')).read()
CFG_OPENAIRE_FORM_TEMPLATE = open(os.path.join(CFG_ETCDIR, 'openaire_form.tpl')).read()

def escape(value, *args, **argd):
    """Always cast to string as to avoid None values."""
    if value is None:
        value = ''
    return cgi_escape(str(value), *args, **argd)

def prepare4js(data):
    """
    Enhance the given dictionary that will be used for string formatting
    with new key prefixed with js_ that will have values where the single
    quote is escaped.
    """
    for key, value in data.items():
        if value:
            data["js_%s" % key] = str(value).replace("'", "\\'")
        else:
            data["js_%s" % key] = value
    return data

RE_PLACEMARKS = re.compile(r'%\((?P<placemark>\w+)\)s')
CFG_OPENAIRE_FORM_TEMPLATE_PLACEMARKS = dict((placemark, '') for placemark in RE_PLACEMARKS.findall(CFG_OPENAIRE_FORM_TEMPLATE))
class Template:
    def tmpl_headers(self, ln):
        return """
            <meta http-equiv="X-UA-Compatible" content="IE=8" />
            <script type="text/javascript">// <![CDATA[
                var gSite = "%(site)s";
                var gLn = "%(ln)s";
            // ]]></script>
            <link type="text/css" href="%(site)s/css/jquery-ui-1.8.14.custom.css" rel="Stylesheet" />
            <link type="text/css" href="%(site)s/css/uploadify.css" rel="Stylesheet" />
            <link type="text/css" href="%(site)s/css/openaire.css" rel="Stylesheet" />
            <script type="text/javascript" src="%(site)s/js/jquery-1.5.2.min.js"></script>
            <script type="text/javascript" src="%(site)s/js/jquery-ui-1.8.14.custom.min.js"></script>
            <script type="text/javascript" src="%(site)s/js/jquery.uploadify.v2.1.4.min.js"></script>
            <script type="text/javascript" src="%(site)s/js/swfobject.js"></script>
            <script type="text/javascript" src="http://cdn.jquerytools.org/1.2.4/all/jquery.tools.min.js"></script>
            <script type="text/javascript" src="%(site)s/js/jquery.elastic.js"></script>
            <script type="text/javascript" src="%(site)s/js/jquery.qtip-1.0.0-rc3.js"></script>
            <script type="text/javascript" src="%(site)s/js/jquery.coolinput.min.js"></script>
            <script type="text/javascript">// <![CDATA[
              jQuery.noConflict();
            // ]]></script>
            <script type="text/javascript" src="%(site)s/js/openaire_deposit_engine.js?v3"></script>
            """ % {'site': CFG_SITE_URL, 'ln': ln}


    def tmpl_choose_project(self, existing_projects=None, selected_project=None, ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)
        if existing_projects is None:
            existing_projects = []
        out = ""
        select_project_title = escape(_("Select a project"))
        if selected_project is not None:
            out += """
                <div class="note">
                    <h3>%(selected_project_title)s</h3>
                    <p>%(selected_project_description)s</p>
                </div>
            """ % {
                'selected_project_title': escape(_("Current Project")),
                'selected_project_description': escape(_("You have currently selected the project %(selected_project)s. Any publication you are currently seeing in this page belong to this project. Any new publication you will start to deposit will as well belong to this project.")) % {'selected_project': selected_project}
            }
            select_project_title = escape(_("Select another project"))
        out += """
            <div class="note">
                <h3>%(select_project_title)s</h3>
            """ % {'select_project_title': select_project_title}
        if existing_projects:
            if selected_project:
                select_project_description = escape(_("This is the list of other projects for which you have already deposited (or begun to deposit) at least one publication. Click on any project to focus on its publications:"))
            else:
                select_project_description = escape(_("This is the list of projects for which you have already deposited (or begun a deposit) at least one publication. Click on any project to focus on its publications:"))
            out += """<p>%(select_project_description)s<br />%(existing_projects)s.</p>""" % {
                'select_project_description': select_project_description,
                'existing_projects': ', '.join(existing_projects)
            }
        out += """
            <p>
                <noscript>
                    <form>
                        <label for="project">%(noscript_description)s</label>
                        <input type="text" name="projectid" size="75" />
                        <input type="submit" value="%(submit)s" />
                    </form>
                </noscript>
                <span style="display: none;" class="yesscript">
                    <form>
                        <label for="project">%(yesscript_description)s</label><br />
                        <input type="text" id="project" name="project" size="75" />
                        <input type="hidden" id="projectid" name="projectid" />
                        <input type="submit" value="%(submit)s" />
                    </form>
                </span>
            </p>
            </div>
            """ % {
                'noscript_description': escape(_("Enter the grant agreement number for the project you wish to select: ")),
                'yesscript_description': escape(_("Start typing the project title or acronym or the grant agreement number for the project you wish to select: ")),
                'submit': escape(_("Select project"), True)
            }
        return out

    def tmpl_focus_on_project(self, existing_projects=None, ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)
        if existing_projects is None:
            return ""
            existing_projects = []
        out = ""
        out = """
            <div class="note">
                <h3>%(focus_on_project_title)s</h3>
                <p>%(select_project_description)s<br />%(existing_projects)s.</p>
            </div>
            """ % {
                'focus_on_project_title': _("Focus on a project"),
                'select_project_description': escape(_("This is the list of projects for which you have already deposited (or begun a deposit) at least one publication. Click on any project to focus on its publications:")),
                'existing_projects': ', '.join(existing_projects),
            }
        return out


    def tmpl_select_a_project(self, existing_projects=None, plus=False, ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)
        if plus:
            openaire_plus = """
                <p>%(explanation)s<br />
                <form method="POST">
                    <input type="hidden" name="projectid" value="000000" />
                    <input type="submit" value="%(no_project)s" />
                </form>
            """ % {
                'explanation': escape(_("If the publications you wish to deposit do not belong"
                    " to any FP7 EU Project, just click the following button.")),
                'no_project': escape(_("No project"), True),
            }
        else:
            openaire_plus = ''
        return """
            <h3>%(select_a_project_label)s</h3>
            <form method="POST">
                %(choose_a_project)s
                <input type="submit" name="ok" id="ok" value="%(select_label)s" />
            </form>
            %(openaire_plus)s
            """ % {
                'select_a_project_label': escape(_("Your projects")),
                'choose_a_project': self.tmpl_choose_project(existing_projects=existing_projects, ln=ln),
                'select_label': escape(_("Select"), True),
                'openaire_plus': openaire_plus
            }

    def tmpl_publication_preview(self, body, recid, ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)
        return """
            <p>%(description)s</p>
            <div class="note">%(body)s</div>
            """ % {
                'description': escape(_("This is a preview of the submitted publication. If approved, it will be available at %(url)s.")) % {
                    "url": """<a href="%(site)s/record/%(recid)s" alt="%(the_record)s">%(site)s/record/%(recid)s</a>""" % {
                        'site': escape(CFG_SITE_URL, True),
                        'recid': recid,
                        'the_record': escape(_("The record"), True),
                    },
                },
                'body': body,
            }


    def tmpl_form(self, publicationid, projectid, projects_information, publication_information, fulltext_information, form=None, metadata_status='empty', warnings=None, errors=None, ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)
        values = dict(CFG_OPENAIRE_FORM_TEMPLATE_PLACEMARKS)
        values['id'] = publicationid
        if form:
            for key, value in form.iteritems():
                if key.endswith('_%s' % publicationid):
                    values['%s_value' % key[:-len('_%s' % publicationid)]] = escape(value, True)
        values['edit_metadata_label'] = escape(_("Edit"))
        values['fulltext_information'] = fulltext_information
        values['projects_information'] = projects_information
        values['site'] = CFG_SITE_URL
        values['mandatory_label'] = escape(_("The symbol %(x_asterisk)s means the field is mandatory.")) % {"x_asterisk": """<img src="%s/img/asterisk.png" alt="mandatory" />""" % CFG_SITE_URL}
        values['language_label'] = escape(_("Document language"))
        values['language_tooltip'] = escape(_("<p>Choose the language that was used to write your document.</p><p>Note that if your document was written in a language different than English you will be able to optionally enter the title and the abstract in their original language.</p>"))
        values['title_label'] = escape(_("English title"))
        values['title_tooltip'] = escape(_("The full title of yor publication in English"))
        values['original_title_label'] = escape(_("Original language title"))
        values['original_title_tooltip'] = escape(_("The full title of your publication in its original language"))
        values['authors_label'] = escape(_("Author(s)"))
        values['authors_tooltip'] = escape(_("<p>Please enter one author per line in the form: <pre>Surname, First Names: Institution</pre> Note that the <em>institution</em> is optional although recommended.</p><p>Example of valid entries are:<ul><li>John, Doe: Example institution</li><li>Jane Doe</li></ul></p>"), True)
        values['authors_hint'] = escape(_("Doe, John: Example institution"))
        values['abstract_label'] = escape(_("English abstract"))
        values['abstract_tooltip'] = escape(_("<p>This is the abstract (i.e. the summary) of your publication, in English.</p><p>Note that, in case of a scientific publication, you can use LaTeX formulas, such as <pre>$\\frac{x^2}{y^3}$</pre> that will be correctly rendered when viewed with a typical browser.</p>"))
        values['english_language_label'] = escape(_("English information"))
        values['original_language_label'] = escape(_("Original language information"))
        values['original_abstract_label'] = escape(_("Original language abstract"))
        values['original_abstract_tooltip'] = escape(_("<p>This is the abstract (i.e. the summary) of your publication, in its original language.</p><p>Note that, in case of a scientific publication, you can use LaTeX formulas, such as <pre>$\\frac{x^2}{y^3}$</pre> that will be correctly rendered when viewed with a typical browser.</p>"))
        values["publication_information_label"] = escape(_("Publication information"))
        values["journal_title_tooltip"] = escape(_("""<p>Start typing part of the name of the journal where you published your publication, and, when possible, it will be automatically completed against a list of known journal titles.</p><p><em>Note that the journal title list has been retrieved from the freely available resource in the <a href="http://www.ncbi.nlm.nih.gov/entrez/citmatch_help.html#JournalLists" target="_blank"><strong>Entrez</strong></a> database.</p>"""), True)
        values['journal_title_label'] = escape(_("Journal title"))
        values['publication_date_label'] = escape(_("Publication date"))
        values['publication_date_tooltip'] = escape(_("This is the official publication date of your document. It's format is <pre>YYYY/MM/DD</pre> such as in <pre>2010/12/25</pre>"""))
        values['volume_label'] = escape(_("Volume"))
        values['volume_tooltip'] = escape(_("The volume part of the publication information, which is typically a number."))
        values['issue_label'] = escape(_("Issue"))
        values['issue_tooltip'] = escape(_("The issue part of the publication information, which is typically a number."))
        values['pages_label'] = escape(_("Pages"))
        values['pages_tooltip'] = escape(_("The pages part of the publication information, which is typically a range of number of the form <pre>123-456</pre>."))
        values['remove_label'] = escape(_("Remove"))
        values['remove_confirm'] = escape(_("Are you sure you want to permanently remove this publication?"))
        values['status_warning_label'] = escape(_('Metadata have some warnings'))
        values['status_error_label'] = escape(_('Metadata have some errors!'))
        values['status_ok_label'] = escape(_('Metadata are OK!'))
        values['submit_label'] = escape(_('Submit this publication'))
        values['form_status'] = 'error' ## FIXME metadata_status
        values['access_rights_options'] = self.tmpl_access_rights_options(values.get('access_rights_value', ''), ln=ln)
        values['access_rights_tooltip'] = escape(_("This is the kind of access rights associated with your publication."))
        values['embargo_date_hint'] = escape(_("End of the embargo"), True)
        values['embargo_date_tooltip'] = escape(_("Enter here the date when the embargo period for this publication will be over."), True)
        values['language_options'] = self.tmpl_language_options(values.get('language_value', 'eng'), ln)
        values['save_label'] = escape(_('Save publication'))
        values['submit_label'] = escape(_('Submit publication'))
        values['embargo_date_size'] = len(values['embargo_date_hint'])
        values['publication_information'] = publication_information
        values['projects_information_label'] = escape(_("Projects information"))
        values['projects_description'] = escape(_("List of projects linked with this publication"))
        values['projects_tooltip'] = escape(_("""<p>This is the list of projects that are associated with this publications.</p><p>Click on the small %(trash_icon)s in order to unlink the corresponding project.</p><p>Start typing a <em>project acronym</em>, a <em>project title</em> or a <em>grant agreement number</em>, choose a project from the menu that will appear and click on the small %(plus_icon)s in order to link a new project to your publication.</p>""") % {
            'trash_icon': """<img src="%s/img/smallbin.gif" alt="Unlink project" />""" % CFG_SITE_URL,
            'plus_icon': """<img src="%s/img/add.png" alt="link project" />""" % CFG_SITE_URL
        }, True)
        values['other_information_label'] = escape(_("Other information"))
        values['keywords_tooltip'] = escape(_("""<p>List of key-words or key-phrases describing this publication.</p><p>Enter an item per line.</p>"""), True)
        values['keywords_label'] = escape(_("Key-words or key-phrases (one per line)."), True)
        values['notes_tooltip'] = escape(_("""Enter here any further information you wish to associate with this document."""), True)
        values["notes_label"] = escape(_("""Notes"""))
        values['status'] = metadata_status
        values['projectid'] = projectid
        if warnings:
            for key, value in warnings.iteritems():
                if key.endswith('_%s' % publicationid):
                    values['warning_%s_value' % key[:-len('_%s' % publicationid)]] = value
        if errors:
            for key, value in errors.iteritems():
                if key.endswith('_%s' % publicationid):
                    values['error_%s_value' % key[:-len('_%s' % publicationid)]] = value

        return CFG_OPENAIRE_FORM_TEMPLATE % values

    def tmpl_access_rights_options(self, selected_access_right, ln=CFG_SITE_LANG):
        from invenio.openaire_deposit_engine import CFG_ACCESS_RIGHTS
        access_rights = CFG_ACCESS_RIGHTS(ln)
        _ = gettext_set_language(ln)
        out = '<option disabled="disabled">%s</option>' % (_("Select access rights"))
        for key, value in access_rights.iteritems():
            if key == selected_access_right:
                out += """<option value="%(key)s" selected="selected">%(value)s</option>""" % {
                    'key': escape(key, True),
                    'value': escape(value)
                }
            else:
                out += """<option value="%(key)s">%(value)s</option>""" % {
                    'key': escape(key, True),
                    'value': escape(value)
                }
        return out

    def tmpl_language_options(self, selected_language='eng', ln=CFG_SITE_LANG):
        from invenio.bibknowledge import get_kb_mappings
        if not selected_language:
            selected_language = 'eng'
        languages = get_kb_mappings('languages')
        _ = gettext_set_language(ln)
        out = ""
        for mapping in languages:
            key = mapping['key']
            value = mapping['value']
            if key == selected_language:
                out += '<option value="%(key)s" selected="selected">%(value)s</option>' % {
                    'key': escape(key, True),
                    'value': escape(value)
                }
            else:
                out += '<option value="%(key)s">%(value)s</option>' % {
                    'key': escape(key, True),
                    'value': escape(value)
                }
        return out

    def tmpl_upload_publications(self, projectid, project_information, session, style, ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)
        data = {
                'noflash_description': escape(_("It looks like you have not installed a recent version of the %(x_fmt_open)sFlash plugin (minimum 9.0.24)%(x_fmt_close)s or that you are using %(x_fmt_open)sGoogle Chrome 10.x/11.x%(x_fmt_close)s or %(x_fmt_open)sChromium 10.x/11.x%(x_fmt_close)s. You will be therefore able to upload only one publication at a time.")) % {
                    'x_fmt_open': "<strong>",
                    'x_fmt_close': "</strong>",
                },
                'upload_publications': escape(_("Upload New Publications")),
                'upload_publications_description': escape(_("Click on %(x_fmt_open)s%(upload)s%(x_fmt_close)s to start uploading one or more publications.")) % {
                    'x_fmt_open': "<strong>",
                    'x_fmt_close': "</strong>",
                    'upload': escape(_("Upload")),
                },
                'site': CFG_SITE_URL,
                'projectid': projectid,
                'session': session,
                'upload': escape(_("Upload")),
                'begin_upload': escape(_("Begin upload")),
                'cancel_upload': escape(_("Cancel upload")),
                'buttontext': _("Upload"),
                'ln': ln,
                'filedescription': _("Publications"),
                'style': style
            }
        if projectid > 0:
            data['upload_publications_description2'] = escape(_("These publications will initially be associated with the project %(project_information)s.")) % {
                'project_information': project_information
            }
        else:
            data['upload_publications_description2'] = ""
        prepare4js(data)
        return """
            <div class="note">
            <h3>%(upload_publications)s</h3>
            <div id="noFlash">
                <form action="%(site)s/deposit/?ln=%(ln)s&style=%(style)s&projectid=%(projectid)s" method="POST" enctype="multipart/form-data">
                <p>%(noflash_description)s</p>
                <p>%(upload_publications_description)s %(upload_publications_description2)s</p>
                <input type="file" name="Filedata" />
                <input type="submit" name="upload" value="%(buttontext)s" />
                </form>
            </div>
            <div id="yesFlash">
                <form action="%(site)s/deposit/?ln=%(ln)s&style=%(style)s" method="POST">
                    <p>%(upload_publications_description)s %(upload_publications_description2)s</p>
                    <input id="fileInput" name="file" type="file" />
                    <input type="reset" value="%(cancel_upload)s" id="cancel_upload"/>
                    <input type="hidden" value="%(projectid)s" name="projectid" />
                    <input type="hidden" value="%(session)s" name="session" />
                </form>
            </div>
            <script type="text/javascript">// <![CDATA[
                if (swfobject.hasFlashPlayerVersion("9.0.24") &&
                        navigator.userAgent.search('Chromium/1(1|0)') < 0) { // There is a bug in Chrom(e|iumt) 10.x/11.x
                    jQuery('#noFlash').hide();
                    jQuery('#yesFlash').show();
                } else {
                    jQuery('#noFlash').show();
                    jQuery('#yesFlash').hide();
                }
                jQuery(document).ready(function() {
                    jQuery('#cancel_upload').hide();
                    jQuery('#fileInput').uploadify({
                        'uploader'  : '%(js_site)s/flash/uploadify.swf',
                        'expressInstall' : '%(js_site)s/flash/expressInstall.swf',
                        'script'    : '%(js_site)s/deposit/uploadifybackend',
                        'cancelImg' : '%(js_site)s/img/cancel.png',
                        'auto'      : true,
                        'folder'    : '/uploads',
                        'multi'     : true,
                        'buttonText': '%(js_buttontext)s',
                        'simUploadLimit': '2',
                        'fileExt': '*.pdf;*.doc;*.docx;*.odt',
                        'fileDesc': '%(js_filedescription)s',
                        'scriptData': {'projectid': '%(js_projectid)s', 'session': '%(js_session)s'},
                        'onAllComplete': function(){
                            jQuery('input.save').trigger('click');
                            window.location="%(js_site)s/deposit/?projectid=%(js_projectid)s&style=%(style)s";
                        },
                        'onOpen': function(){
                            jQuery('#cancel_upload').show();
                        }
                    });
                    jQuery('#cancel_upload').click(function(){
                        jQuery('#fileInput').uploadifyClearQueue();
                        return 0;
                    });
                });
            // ]]></script>
            </div>""" % data


    def tmpl_publication_information(self, publicationid, title, authors, abstract, ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)
        authors = authors.strip().splitlines()
        if not title:
            title = _("Title not yet defined")
        data = {
                'title_label': escape(_("Title")),
                'authors_label': len(authors) != 1 and escape(_("Author(s)")) or escape(_("Author")),
                'abstract_label': escape(_("Abstract")),
                'title': escape(title),
                'authors': "<br />".join([escape(author) for author in authors]),
                'abstract': escape(abstract).replace('\n', '<br />'),
                'id': escape(publicationid, True)
            }
        data['body'] = """<div id="publication_information_%(id)s" class="publication_information">%(title)s</div>""" % data
        prepare4js(data)
        return """
            %(body)s
            <script type="text/javascript">// <![CDATA[
                jQuery(document).ready(function(){
                    var tooltip = clone(gTipDefault);
                    tooltip.content = {
                        'text': '<table><tbody><tr><td align="right"><strong>%(js_title_label)s:<strong></td><td align="left">%(js_title)s</td></tr><tr><td align="right"><strong>%(js_authors_label)s:<strong></td><td align="left">%(js_authors)s</td></tr><tr><td align="right"><strong>%(js_abstract_label)s:<strong></td><td align="left">%(js_abstract)s</td></tr><tbody></table>'
                    };
                    jQuery('#publication_information_%(id)s').qtip(tooltip);
                });
            // ]]></script>""" % data

    def tmpl_project_information(self, global_projectid, projectid, existing_publications, grant_agreement_number='', ec_project_website='', acronym='', call_identifier='', end_date='', start_date='', title='', fundedby='', deletable=True, linked=True, publicationid=None, style='invenio', ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)
        if projectid == 0:
            acronym = _('NO PROJECT')
        if not acronym:
            acronym = title
        out = """<span class="selectedproject" id="project_%(id)s_%(publicationid)s">"""
        if linked:
            out += """<a href="%(site)s/deposit?projectid=%(id)s&amp;ln=%(ln)s&amp;style=%(style)s">%(acronym)s (%(existing_publications)s)</a>"""
        else:
            out += """<strong>%(acronym)s</strong>"""
        out += """</span>"""
        if projectid > 0:
            out += """
                <script type="text/javascript">// <![CDATA[
                    jQuery(document).ready(function(){
                        var tooltip = clone(gTipDefault);
                        tooltip.content = {
                            'text': '<table><tbody><tr><td align="right"><strong>%(js_acronym_label)s:<strong></td><td align="left">%(js_acronym)s</td></tr><tr><td align="right"><strong>%(js_title_label)s:<strong></td><td align="left">%(js_title)s</td></tr><tr><td align="right"><strong>%(js_grant_agreement_number_label)s:<strong></td><td align="left">%(js_grant_agreement_number)s</td></tr>%(ec_project_website_row)s<tr><td align="right"><strong>%(js_start_date_label)s:<strong></td><td align="left">%(js_start_date)s</td></tr><tr><td align="right"><strong>%(js_end_date_label)s:<strong></td><td align="left">%(js_end_date)s</td></tr><tr><td align="right"><strong>%(js_fundedby_label)s:<strong></td><td align="left">%(js_fundedby)s</td></tr><tr><td align="right"><strong>%(js_call_identifier_label)s:<strong></td><td align="left">%(js_call_identifier)s</td></tr><tbody></table>'
                        };
                        jQuery('#project_%(js_id)s_%(js_publicationid)s').qtip(tooltip);
                    });
                // ]]></script>"""
        if deletable:
            out += """
                <noscript>
                    <a href="%(site)s/deposit?projectid=%(global_projectid)s&amp;publicationid=%(publicationid)s&amp;unlinkproject=%(id)s&amp;ln=%(ln)s&amp;style=%(style)s"><img src="%(site)s/img/delete.png" title="%(delete_project_label)s" alt="%(delete_project_label)s" /></a>
                </noscript>
                <img src="%(site)s/img/delete.png" title="%(delete_project_label)s" alt="%(delete_project_label)s" id="delete_%(id)s_%(publicationid)s" class="hidden" />
                <script type="text/javascript">// <![CDATA[
                    jQuery(document).ready(function(){
                        jQuery("#delete_%(js_id)s_%(js_publicationid)s").click(function(){
                            var data = {};
                            data.projectid = %(js_id)s;
                            data.publicationid = "%(js_publicationid)s";
                            data.action = "unlinkproject";
                            if (confirm("%(js_confirm_delete_project)s"))
                                jQuery.post(gSite + '/deposit/ajaxgateway', data, elaborateAjaxGateway, "json");
                            return false;
                        }).show();
                    });
                // ]]></script>"""
        data = {
            'id': escape(projectid, True),
            'publicationid': escape(publicationid, True),
            'site': escape(CFG_SITE_URL, True),
            'ln': escape(ln, True),
            'acronym': escape(acronym),
            'acronym_label': escape(_("Acronym"), True),
            'existing_publications': escape(existing_publications),
            'title_label': escape(_("Title"), True),
            'title': escape(title, True),
            'grant_agreement_number_label': escape(_("Grant Agreement Number"), True),
            'grant_agreement_number': escape(str(grant_agreement_number), True),
            'ec_project_website_label': escape(_("EC Project Website"), True),
            'ec_project_website': escape(ec_project_website, True),
            'start_date_label': escape(_("Start Date"), True),
            'start_date': escape(start_date, True),
            'end_date_label': escape(_("End Date"), True),
            'end_date': escape(end_date, True),
            'fundedby_label': escape(_("Funded By"), True),
            'fundedby': escape(fundedby, True),
            'call_identifier_label': escape(_("Call Identifier"), True),
            'call_identifier': escape(call_identifier, True),
            'global_projectid': escape(global_projectid, True),
            'confirm_delete_project': escape(_("Are you really sure you want to unlink this publication from the project %(acronym)s?") % {'acronym': acronym}, True),
            'delete_project_label': escape(_("Unlink project %(acronym)s") % {'acronym': acronym}, True),
            'style': style,
        }
        prepare4js(data)
        ## We add the ec_project_website_row only if there is indeed a project website
        data['ec_project_website_row'] = ec_project_website and ("""<tr><td align="right"><strong>%(js_ec_project_website_label)s:<strong></td><td align="left"><a href="%(js_ec_project_website)s" target="_blank">%(js_ec_project_website_label)s</a></td></tr>""" % data) or ""

        return out % data


    def tmpl_projects_box(self, publicationid, associated_projects, ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)

        associated_projects = ' '.join(associated_projects)

        out = """
            <div id="projectsbox_%(id)s">
                %(associated_projects)s
                <noscript>
                    <label for="linkproject_%(id)s">Grant Agreement Number</label>
                </noscript>
                <input type="text" name="linkproject" id="linkproject_%(id)s" size="30" />
                <input type="hidden" name="dummy" id="linkproject_%(id)s_hidden" />
                <input type="hidden" name="publicationid" value="%(id)s" />
                <!-- <img src="%(site)s/img/add.png" alt="%(link_project)s" id="projectsbox_submit_%(id)s" /> -->
            </div>
            <script type="text/javascript">//<![CDATA[
                jQuery(document).ready(function() {
                    jQuery('#linkproject_%(js_id)s').each(function() {
                        // Since Javascript is working, lets disable sending
                        // the text filled up by the user, and instead
                        // let's consider what is filled by the autocomplete plugin
                        // inside the hidden field.
                        this.name = "dummy";
                    });
                    jQuery('#linkproject_%(js_id)s_hidden').each(function() {
                        this.name = "linkproject";
                    });
                    jQuery('#linkproject_%(js_id)s').coolinput({
                            hint: "%(js_hint)s"
                        }).autocomplete({
                        source: gSite + "/kb/export?kbname=projects&format=jquery&limit=20&ln=" + gLn,
                        focus: function(event, ui) {
                            jQuery('#linkproject_%(js_id)s').val(ui.item.label);
                            return false;
                        },
                        select: function(event, ui) {
                            jQuery('#linkproject_%(js_id)s').val(ui.item.label);
                            jQuery('#linkproject_%(js_id)s_hidden').val(ui.item.value);
                            var data = {};
                            data.projectid = jQuery('#linkproject_%(js_id)s_hidden').val();
                            data.publicationid = "%(js_id)s";
                            data.action = "linkproject";
                            jQuery.post(gSite + '/deposit/ajaxgateway', data, elaborateAjaxGateway, "json");
                            return false;
                        }
                    });
                    jQuery("#projectsbox_submit_%(js_id)s").click(function(){
                        var data = {};
                        data.projectid = jQuery('#linkproject_%(js_id)s_hidden').val();
                        data.publicationid = "%(js_id)s";
                        data.action = "linkproject";
                        jQuery.post(gSite + '/deposit/ajaxgateway', data, elaborateAjaxGateway, "json");
                        return false;
                    });
                });
            //]]></script>"""
        data = {
            "id": publicationid,
            "associated_projects": associated_projects,
            "site": CFG_SITE_URL,
            "link_project": escape(_("Link project")),
            "hint": escape(_("Start typing the project name..."))
        }
        data = prepare4js(data)
        return out % data

    def tmpl_add_publication_data_and_submit(self, projectid, publication_forms, submitted_publications, project_information, ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)

        out = ""
        if publication_forms:
            publication_forms = """<form method="POST" id="publication_forms" accept-charset="UTF-8">
            <div class="OpenAIRE">
            <table width="100%%">
            %(publication_forms)s
            </table>
            </div>
            </form>""" % {'publication_forms': publication_forms}

            out += """
                <div class="note">
                <h3>%(title)s</h3>
                <p>%(description)s</p>
                %(publication_forms)s
                <script type="text/javascript">//<![CDATA[
                    var gProjectid = "%(js_projectid)s";
                    jQuery(document).ready(function(){
                        jQuery('input.datepicker').datepicker({
                            dateFormat: 'yy-mm-dd',
                            showOn: 'both',
                            onClose: function(){
                                jQuery(this).focus();
                            },
                            showButtonPanel: true
                        });
                        jQuery('textarea').elastic();
                        jQuery('#publication_forms').submit(function(event){
                            event.preventDefault();
                            return false;
                        });
                        jQuery('a.deletepublication').click(function(){
                            return confirm("%(js_confirm_delete_publication)s");
                        });
                    });
                //]]></script>
                </div>
                """
        out += """
        <div id="submitted_publications" class="note">
        <h3>%(submitted_publications_title)s</h3>
        %(submitted_publications)s
        </div>
        <script type="text/javascript">//<![CDATA[
            jQuery(document).ready(function(){
                if (%(hide_submitted_publications_section)s)
                    jQuery("#submitted_publications").hide();
            });
        //]]> </script>
        """
        if projectid:
            description = escape(_('These are the publications you are depositing for the project %s')) % (project_information)
        else:
            description = escape(_('These are the publications you are depositing for which you have not yet associated any project.'))
        data = {
            'submitted_publications_title': escape(_("Successfully submitted publications")),
            'title': escape(_('Your Current Publications')),
            'selected_project_title': escape(_("Selected Project")),
            'projectid': projectid,
            'change_project_label': escape(_('change project'), True),
            'uploaded_publications': escape(_('Uploaded Publications')),
            'title_head': escape(_('Title')),
            'license_type_head': escape(_('License Type')),
            'embargo_release_date_head': escape(_('Embargo%(x_br)sRelease Date')) % {'x_br': '<br />'},
            'publication_forms': publication_forms,
            'confirm_delete_publication': _("Are you sure you want to delete this publication?"),
            'submitted_publications': submitted_publications,
            'hide_submitted_publications_section': submitted_publications and "false" or "true",
            'ln': ln,
            'projectid': projectid,
            'done': escape(_("Done"), True),
            'today': escape(_("Today"), True),
            'next': escape(_("Next"), True),
            'prev': escape(_("Prev"), True),
            'site': escape(CFG_SITE_URL, True),
            'description': description
        }
        data = prepare4js(data)
        return out % data


    def tmpl_fulltext_information(self, filename, publicationid, download_url, md5, mimetype, format, size, ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)
        filename = filename.decode('utf8')
        filename = ''.join(["%s<br />" % escape(filename[i:i+30].encode('utf8')) for i in xrange(0, len(filename), 30)])
        data = {
                'file_label': escape(_('file')),
                'id': escape(publicationid, True),
                'filename': filename,
                'filename_label': escape(_("Name")),
                'download_url': escape(download_url, True),
                'mimetype': escape(mimetype, True),
                'mimetype_label': escape(_("Mimetype")),
                'format': escape(format),
                'format_label': escape(_("Format")),
                'size_label': escape(_("Size")),
                'size': escape(nice_size(size)),
                'checksum_label': escape(_("MD5 Checksum")),
                'md5': escape(md5),
            }
        prepare4js(data)
        return """
            %(file_label)s: <div class="file" id="file_%(id)s"><em>%(filename)s</em></div>
            <script type="text/javascript">//<![CDATA[
                jQuery(document).ready(function(){
                    var tooltip = clone(gTipDefault);
                    tooltip.content = {
                        'text': '<table><tbody><tr><td align="right"><strong>%(js_filename_label)s:<strong></td><td align="left"><a href="%(js_download_url)s" target="_blank" type="%(js_mimetype)s">%(js_filename)s</a></td></tr><tr><td align="right"><strong>%(js_format_label)s:<strong></td><td align="left">%(js_format)s</td></tr><tr><td align="right"><strong>%(js_size_label)s:<strong></td><td align="left">%(js_size)s</td></tr><tr><td align="right"><strong>%(js_mimetype_label)s:<strong></td><td align="left">%(js_mimetype)s</td></tr><tr><td align="right"><strong>%(js_checksum_label)s:<strong></td><td align="left">%(js_md5)s</td></tr><tbody></table>'
                    };
                    jQuery('#file_%(id)s').qtip(tooltip);
                });
            //]]></script>""" % data

    def tmpl_page(self, title, body, headers, username, portalurl, return_value, project_information, ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)
        if not project_information:
            crumbs = """\
<img src="%(portalurl)s/templates/yoo_level/images/arrow.png" alt="" />
%(to_orphan_repository)s""" % {
    'portalurl': portalurl,
    'to_orphan_repository': escape(_("to orphan repository"))
}
        else:
            crumbs = """\
<img src="%(portalurl)s/templates/yoo_level/images/arrow.png" alt="" />
<a href="/deposit?ln=%(ln)s">%(to_orphan_repository)s</a>
<img src="%(portalurl)s/templates/yoo_level/images/arrow.png" alt="" />
%(project_information)s
""" % {
    'portalurl': portalurl,
    'to_orphan_repository': escape(_("to orphan repository")),
    'ln': ln,
    'project_information': project_information
}


        return CFG_OPENAIRE_PAGE_TEMPLATE % {
            'headers': headers,
            'title': title,
            'body': body,
            'username': escape(username),
            'portalurl': escape(portalurl, True),
            'return': escape(return_value, True),
            'site': CFG_SITE_URL,
            'crumbs': crumbs,
            'release': "Invenio %s" % CFG_VERSION}

    def tmpl_confirmation_email_body(self, title, authors, url, report_numbers, ln=CFG_SITE_LANG):
        _ = gettext_set_language(ln)
        return _("""\
this is to confirm that you successfully deposited a publication into OpenAIRE:

    title: %(title)s
    authors: %(authors)s
    url: <%(url)s>

OpenAIRE Orphan Record Repository curators will soon review your deposition and
eventually approve it.

If approved, you will be able to cite this publication using
one of the following report numbers, that were automatically
assigned to your document:

    %(report_numbers)s

If you wish to deposit other documents, please visit:
    <%(site)s/deposit>
""") % {
        'title': title,
        'authors': ', '.join(authors),
        'url': url,
        'site': CFG_SITE_URL,
        'report_numbers': ', '.join(report_numbers)
        }

    def tmpl_curators_email_body(self, title, authors, url, bibedit_url):
        return """\
this is to let you know that a new publication has just been deposited into
OpenAIRE and is waiting for your approval:

    title: %(title)s
    authors: %(authors)s
    url: <%(url)s>

In order to approve it, open it with BibEdit at this URL:
    <%(bibedit_url)s>

and change its collection definition (tag 980__a) from PROVISIONAL to OPENAIRE.

In order to reject it change its collection definition (tag 980__a) from
PROVISIONAL to REJECTED.
""" % {
        'title': title,
        'authors': ', '.join(authors),
        'url': url,
        'bibedit_url': bibedit_url
        }