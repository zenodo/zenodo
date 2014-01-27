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

"""BibFormat element - Prints a table of files
"""

import re
from flask import current_app
from invenio.legacy.bibdocfile.api import BibRecDocs, file_strip_ext, normalize_format, compose_format
from invenio.legacy.bibdocfile.config import CFG_BIBDOCFILE_ICON_SUBFORMAT_RE
from invenio.base.i18n import gettext_set_language
from cgi import escape, parse_qs
from urlparse import urlparse
from os.path import basename
import urllib
from invenio.ext.template import render_template_to_string


def format_element(bfo, template='bfe_files.html', show_subformat_icons='yes',
        focus_on_main_file='no', **kwargs):
    """
    This is the default format for formatting fulltext links.

    When possible, it returns only the main file(s) (+ link to
    additional files if needed). If no distinction is made at
    submission time between main and additional files, returns
    all the files
    """

    # Retrieve files
    (parsed_urls, old_versions, additionals) = get_files(bfo, \
        distinguish_main_and_additional_files=focus_on_main_file.lower() == 'yes',
        include_subformat_icons=show_subformat_icons == 'yes')

    ctx = {
        'recid': bfo.recID,
        'bfo': bfo,
        'others_urls': parsed_urls['others_urls'],
        'main_urls': parsed_urls['main_urls'],
    }

    kwargs.update(ctx)

    return render_template_to_string(template, **kwargs)


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

def get_files(bfo, distinguish_main_and_additional_files=True,
        include_subformat_icons=False):
    """
    Returns the files available for the given record.
    Returned structure is a tuple (parsed_urls, old_versions, additionals):
     - parsed_urls: contains categorized URLS (see details below)
     - old_versions: set to True if we can have access to old versions
     - additionals: set to True if we have other documents than the 'main' document

     Parameter 'include_subformat_icons' decides if subformat
     considered as icons should be returned

    'parsed_urls' is a dictionary in the form::
        {'main_urls' : {'Main'      : [('http://CFG_SITE_URL/CFG_SITE_RECORD/1/files/aFile.pdf', 'aFile', 'PDF'),
                                       ('http://CFG_SITE_URL/CFG_SITE_RECORD/1/files/aFile.gif', 'aFile', 'GIF')],
                        'Additional': [('http://CFG_SITE_URL/CFG_SITE_RECORD/1/files/bFile.pdf', 'bFile', 'PDF')]},

         'other_urls': [('http://externalurl.com/aFile.pdf', 'Fulltext'),      # url(8564_u), description(8564_z/y)
                        ('http://externalurl.com/bFile.pdf', 'Fulltext')],

         'cern_urls' : [('http://cern.ch/aFile.pdf', 'Fulltext'),              # url(8564_u), description(8564_z/y)
                        ('http://cern.ch/bFile.pdf', 'Fulltext')],
        }

    Some notes about returned structure:
        - key 'cern_urls' is only available on CERN site
        - keys in main_url dictionaries are defined by the BibDoc.
        - older versions are not part of the parsed urls
        - returns only main files when possible, that is when doctypes
          make a distinction between 'Main' files and other
          files. Otherwise returns all the files as main. This is only
          enabled if distinguish_main_and_additional_files is set to True
    """
    CFG_SITE_URL = current_app.config['CFG_SITE_URL']
    CFG_CERN_SITE = current_app.config['CFG_CERN_SITE']
    CFG_BIBFORMAT_HIDDEN_FILE_FORMATS = current_app.config['CFG_BIBFORMAT_HIDDEN_FILE_FORMATS']
    _CFG_NORMALIZED_BIBFORMAT_HIDDEN_FILE_FORMATS = set(normalize_format(fmt) for fmt in CFG_BIBFORMAT_HIDDEN_FILE_FORMATS)

    _ = gettext_set_language(bfo.lang)

    urls = bfo.fields("8564_")
    bibarchive = BibRecDocs(bfo.recID)

    old_versions = False # We can provide link to older files. Will be
                         # set to True if older files are found.
    additionals = False  # We have additional files. Will be set to
                         # True if additional files are found.

    # Prepare object to return
    parsed_urls = {'main_urls':{},    # Urls hosted by Invenio (bibdocs)
                  'others_urls':[]    # External urls
                  }
    if CFG_CERN_SITE:
        parsed_urls['cern_urls'] = [] # cern.ch urls

    # Doctypes can of any type, but when there is one file marked as
    # 'Main', we consider that there is a distinction between "main"
    # and "additional" files. Otherwise they will all be considered
    # equally as main files
    distinct_main_and_additional_files = False
    if len(bibarchive.list_bibdocs(doctype='Main')) > 0 and \
           distinguish_main_and_additional_files:
        distinct_main_and_additional_files = True
    # Parse URLs
    for complete_url in urls:
        if complete_url.has_key('u'):
            url = complete_url['u']
            (dummy, host, path, dummy, params, dummy) = urlparse(url)
            subformat = complete_url.get('x', '')
            filename = urllib.unquote(basename(path))
            name = file_strip_ext(filename)
            url_format = filename[len(name):]
            if url_format.startswith('.'):
                url_format = url_format[1:]
            if compose_format(url_format, subformat) in _CFG_NORMALIZED_BIBFORMAT_HIDDEN_FILE_FORMATS:
                ## This format should be hidden.
                continue

            descr = _("Fulltext")
            if complete_url.has_key('y'):
                descr = complete_url['y']
                if descr == 'Fulltext':
                    descr = _("Fulltext")
            if not url.startswith(CFG_SITE_URL): # Not a bibdoc?
                if not descr: # For not bibdoc let's have a description
                    # Display the URL in full:
                    descr = url
                if CFG_CERN_SITE and 'cern.ch' in host and \
                       ('/setlink?' in url or \
                        'cms' in host or \
                        'documents.cern.ch' in url or \
                        'doc.cern.ch' in url or \
                        'preprints.cern.ch' in url):
                    url_params_dict = dict([part.split('=') for part in params.split('&') if len(part.split('=')) == 2])
                    if url_params_dict.has_key('categ') and \
                           (url_params_dict['categ'].split('.', 1)[0] in cern_arxiv_categories) and \
                           url_params_dict.has_key('id'):
                        # Old arXiv links, used to be handled by
                        # setlink. Provide direct links to arXiv
                        for file_format, label in [('pdf', "PDF")]:#,
                            #('ps', "PS"),
                            #('e-print', "Source (generally TeX or LaTeX)"),
                            #('abs', "Abstract")]:
                            url = "http://arxiv.org/%(format)s/%(category)s/%(id)s" % \
                                  {'format': file_format,
                                   'category': url_params_dict['categ'],
                                   'id': url_params_dict['id']}
                            parsed_urls['others_urls'].append((url, "%s/%s %s" % \
                                                               (url_params_dict['categ'],
                                                                url_params_dict['id'],
                                                                label)))
                else:
                    parsed_urls['others_urls'].append((url, descr)) # external url
            else: # It's a bibdoc!
                assigned = False
                for doc in bibarchive.list_bibdocs():
                    if int(doc.get_latest_version()) > 1:
                        old_versions = True
                    if True in [f.get_full_name().startswith(filename) \
                                    for f in doc.list_all_files()]:
                        assigned = True
                        if not include_subformat_icons and \
                               CFG_BIBDOCFILE_ICON_SUBFORMAT_RE.match(subformat):
                            # This is an icon and we want to skip it
                            continue
                        if not doc.get_doctype(bfo.recID) == 'Main' and \
                               distinct_main_and_additional_files == True:
                            # In that case we record that there are
                            # additional files, but don't add them to
                            # returned structure.
                            additionals = True
                        else:
                            if not descr:
                                descr = _('Fulltext')
                            if not parsed_urls['main_urls'].has_key(descr):
                                parsed_urls['main_urls'][descr] = []
                            params_dict = parse_qs(params)
                            if 'subformat' in params_dict:
                                url_format += ' (%s)' % params_dict['subformat'][0]
                            parsed_urls['main_urls'][descr].append((url, name, url_format))
                if not assigned: # Url is not a bibdoc :-S
                    if not descr:
                        descr = filename
                    parsed_urls['others_urls'].append((url, descr)) # Let's put it in a general other url
    return (parsed_urls, old_versions, additionals)

_RE_SPLIT = re.compile(r"\d+|\D+")
def sort_alphanumerically(elements):
    elements = [([not token.isdigit() and token or int(token) for token in _RE_SPLIT.findall(element)], element) for element in elements]
    elements.sort()
    return [element[1] for element in elements]
