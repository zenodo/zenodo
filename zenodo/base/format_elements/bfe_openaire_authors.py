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

"""OpenAIRE specific authors printing
"""

import re
from urllib import quote
from cgi import escape
from flask import current_app
from invenio.base.i18n import gettext_set_language

def format_element(bfo, limit, separator=' ; ',
           extension='[...]',
           print_links="yes",
           print_affiliations='no',
           affiliation_prefix=' (',
           affiliation_suffix=')',
           interactive="no",
           highlight="no",
           link_author_pages="no",
           relator_code_pattern=None):
    """
    Prints the list of authors of a record.

    @param limit: the maximum number of authors to display
    @param separator: the separator between authors.
    @param extension: a text printed if more authors than 'limit' exist
    @param print_links: if yes, prints the authors as HTML link to their publications
    @param print_affiliations: if yes, make each author name followed by its affiliation
    @param affiliation_prefix: prefix printed before each affiliation
    @param affiliation_suffix: suffix printed after each affiliation
    @param interactive: if yes, enable user to show/hide authors when there are too many (html + javascript)
    @param highlight: highlights authors corresponding to search query if set to 'yes'
    @param relator_code_pattern: a regular expression to filter authors based on subfield $4 (relator code)
    """
    _ = gettext_set_language(bfo.lang)    # load the right message language
    CFG_SITE_URL = current_app.config['CFG_SITE_URL']

    authors = []
    authors_1 = bfo.fields('100__')
    authors_2 = bfo.fields('700__')

    authors.extend(authors_1)
    authors.extend(authors_2)

    if relator_code_pattern:
        p = re.compile(relator_code_pattern)
        authors = filter(lambda x: p.match(x.get('4', '')), authors)

    nb_authors = len(authors)

    bibrec_id = bfo.control_field("001")

    # Process authors to add link, highlight and format affiliation
    for author in authors:

        if author.has_key('a'):
            if highlight == 'yes':
                from invenio import bibformat_utils
                author['a'] = bibformat_utils.highlight(author['a'],
                                                        bfo.search_pattern)

            if print_links.lower() == "yes":
                if link_author_pages == "no":
                    author['a'] = '<a itemprop="creator" href="' + CFG_SITE_URL + \
                                  '/search?f=author&amp;p=' + quote(author['a']) + \
                                  '&amp;ln=' + bfo.lang + \
                                  '" ><span itemscope itemtype="http://schema.org/Person"><span itemprop="name">' + escape(author['a']) + '</span></span></a>'
                else:
                    author['a'] = '<a itemprop="creator" rel="author" href="' + CFG_SITE_URL + \
                                  '/author/' + quote(author['a']) + \
                                  '?recid=' +  bibrec_id + \
                                  '&ln=' + bfo.lang + \
                                  '">' + escape(author['a']) + '</a>'

        if author.has_key('u'):
            if print_affiliations == "yes":
                author['u'] = affiliation_prefix + '<span itemprop="affiliation">' + author['u'] + \
                              '<span>' + affiliation_suffix

    # Flatten author instances
    if print_affiliations == 'yes':
        authors = [author.get('a', '') + author.get('u', '')
                   for author in authors]
    else:
        authors = [author.get('a', '')
                   for author in authors]

    if limit.isdigit() and  nb_authors > int(limit) and interactive != "yes":
        return separator.join(authors[:int(limit)]) + extension

    elif limit.isdigit() and nb_authors > int(limit) and interactive == "yes":
        out = '<a name="show_hide" />'
        out += separator.join(authors[:int(limit)])
        out += '<span id="more_%s" style="">' % bibrec_id + separator + \
               separator.join(authors[int(limit):]) + '</span>'
        out += ' <span id="extension_%s"></span>' % bibrec_id
        out += ' <small><i><a id="link_%s" href="#" style="color:rgb(204,0,0);"></a></i></small>' % bibrec_id
        out += '''
        <script type="text/javascript">
        $('#link_%(recid)s').click(function(event) {
            event.preventDefault();
            var more = document.getElementById('more_%(recid)s');
            var link = document.getElementById('link_%(recid)s');
            var extension = document.getElementById('extension_%(recid)s');
            if (more.style.display=='none'){
                more.style.display = '';
                extension.style.display = 'none';
                link.innerHTML = "%(show_less)s"
            } else {
                more.style.display = 'none';
                extension.style.display = '';
                link.innerHTML = "%(show_more)s"
            }
            link.style.color = "rgb(204,0,0);"
        });

        function set_up_%(recid)s(){
            var extension = document.getElementById('extension_%(recid)s');
            extension.innerHTML = "%(extension)s";
            $('#link_%(recid)s').click();
        }

        </script>
        ''' % {'show_less':_("Hide"),
             'show_more':_("Show all %i authors") % nb_authors,
             'extension':extension,
             'recid': bibrec_id}
        out += '<script type="text/javascript">set_up_%s()</script>' % bibrec_id

        return out
    elif nb_authors > 0:
        return separator.join(authors)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
