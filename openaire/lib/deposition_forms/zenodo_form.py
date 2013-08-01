# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA

from wtforms import validators
from invenio.webinterface_handler_flask_utils import _
from invenio.webdeposit_form import WebDepositForm as Form
from invenio.webdeposit_field_widgets import date_widget, plupload_widget, \
    ButtonWidget
from flask.ext import wtf
from invenio import openaire_validators as oa_validators
from invenio.config import CFG_SITE_NAME, CFG_SITE_SUPPORT_EMAIL
from datetime import datetime, date
from jinja2 import Markup

# Import custom fields
from invenio.webdeposit_load_fields import fields

__all__ = ['ZenodoForm']


#
# WTForm filters
#
def strip_string(data):
    if isinstance(data, basestring):
        return data.strip()
    else:
        return data


def strip_doi(data):
    """
    Remove "doi:" prefix from string
    """
    if isinstance(data, basestring):
        if data.lower().startswith("doi:"):
            return data[4:]
    return data


def splitchar_list(c):
    def _inner(data):
        if isinstance(data, basestring):
            newdata = []
            for item in data.split(c):
                if item.strip():
                    newdata.append(item.strip().encode('utf8'))
            return newdata
        else:
            return data
    return _inner


def splitlines_list(data):
    if isinstance(data, basestring):
        newdata = []
        for line in data.splitlines():
            if line.strip():
                newdata.append(line.strip().encode('utf8'))
        return newdata
    else:
        return data


def map_func(func):
    def _mapper(data):
        if isinstance(data, list):
            return map(func, data)
        else:
            return data
    return _mapper

#
# ZENODO Upload Form
#
class ZenodoForm(Form):

    #
    # Fields
    #
    upload_type = fields.UploadTypeField(validators=[validators.required()])
    publication_type = fields.SelectField(
        label='Type of publication',
        choices=[
            ('book', 'Book'),
            ('section', 'Book section'),
            ('conferencepaper', 'Conference paper'),
            ('article', 'Journal article'),
            ('patent', 'Patent'),
            ('preprint', 'Preprint'),
            ('report', 'Report'),
            ('softwaredocumentation', 'Software documentation'),
            ('thesis', 'Thesis'),
            ('technicalnote', 'Technical note'),
            ('workingpaper', 'Working paper'),
            ('other', 'Other'),
        ],
        validators=[
            oa_validators.RequiredIf('upload_type', ['publication']),
            validators.optional()
        ],
        hidden=True,
        disabled=True,
    )
    image_type = fields.SelectField(
        label='Type of image',
        choices=[
            ('figure', 'Figure'),
            ('plot', 'Plot'),
            ('drawing', 'Drawing'),
            ('diagram', 'Diagram'),
            ('photo', 'Photo'),
            ('other', 'Other'),
        ],
        validators=[
            oa_validators.RequiredIf('upload_type', ['image']),
            validators.optional()
        ],
        hidden=True,
        disabled=True,
    )

    #
    # Collection
    #
    collections = fields.CollectionsField(
        label="Communities",
        description="Optional.",
        filters=[
            splitchar_list(","),
        ],
        placeholder="Start typing a community name...",
    )

    #
    # Basic information
    #
    doi = fields.DOIField(
        label="Digital Object Identifier",
        description="Optional. Did your publisher already assign a DOI to your"
            " upload? If not, leave the field empty and we will register a new"
            " DOI for you. A DOI allow others to easily and unambiguously cite"
            " your upload.",
        filters=[
            strip_string,
            strip_doi,
        ],
        placeholder="e.g. 10.1234/foo.bar...",
    )

    prereserve_doi = fields.ReserveDOIField(
        label="",
        doi_field="doi",
        widget=ButtonWidget(
            label=_("Pre-reserve DOI"),
            icon='icon-barcode',
            tooltip=_('Pre-reserve a Digital Object Identifier for your upload. This allows you know the DOI before you submit your upload, and can thus include it in e.g. publications. The DOI is not finally registered until submit your upload.'),
        ),
    )

    publication_date = fields.Date(
        label=_('Publication date'),
        description='Required. Format: YYYY-MM-DD. The date your upload was '
            'made available in case it was already published elsewhere.',
        default=date.today(),
        validators=[validators.required()],
        widget=date_widget,
    )
    title = fields.TitleField(
        validators=[validators.required()],
        description='Required.',
        filters=[
            strip_string,
        ],
    )
    creators = fields.AuthorField(
        label="Authors",
        validators=[validators.required()],
        description="Required. Format: Family name, First name: Affiliation"
            " (one author per line)",
        placeholder="Family name, First name: Affiliation (one author per line)",
    )
    description = fields.AbstractField(
        label="Description",
        description='Required.',
        validators=[validators.required()],
        filters=[
            strip_string,
        ],
    )
    keywords = fields.KeywordsField(
        validators=[validators.optional()],
        description="Optional. Format: One keyword per line.",
        filters=[
            splitlines_list
        ],
        placeholder="One keyword per line...",
    )
    notes = fields.TextAreaField(
        label="Additional notes",
        description='Optional.',
        validators=[validators.optional()],
        filters=[
            strip_string,
        ],
    )

    #
    # Access rights
    #
    access_right = fields.AccessRightField(
        label="Access right",
        description="Required. Open access uploads have considerably higher "
            "visibility on %s." % CFG_SITE_NAME,
        default="open",
        validators=[validators.required()]
    )
    embargo_date = fields.Date(
        label=_('Embargo date'),
        description='Required only for Embargoed Access uploads. Format: '
            'YYYY-MM-DD. The date your upload will be made publicly available '
            'in case it is under an embargo period from your publisher.',
        default=date.today(),
        validators=[
            oa_validators.RequiredIf('access_right', ['embargoed']),
            validators.optional()
        ],
        widget=date_widget,
        hidden=True,
        disabled=True,
    )
    license = fields.LicenseField(
        validators=[
            oa_validators.RequiredIf('access_right', ['embargoed', 'open', ]),
            validators.required()
        ],
        default='cc-zero',
        domain_data=True,
        domain_content=True,
        domain_software=False,
        description='Required. The selected license applies to all of your '
            'files displayed in the bottom of the form. If you want to upload '
            'some files under a different license, please do so in two separate'
            ' uploads. If you think a license missing in the list, please '
            'inform us at %s.' % CFG_SITE_SUPPORT_EMAIL,
        filters=[
            strip_string,
        ],
        placeholder="Start typing a license name or abbreviation...",
    )

    #
    # Funding
    #
    funding_source = fields.FundingField(
        label="Grants",
        description="Optional. Note, a human %s curator will validate your upload before reporting it to OpenAIRE, and you may thus experience a delay before your upload is available in OpenAIRE." % CFG_SITE_NAME,
        filters=[
            splitchar_list(","),
        ],
        placeholder="Start typing a grant number, name or abbreviation...",
    )

    #
    # Related work
    #
    related_identifiers = fields.RelatedIdentifiersField(
        label="Related identifiers",
        filters=[
            splitlines_list,
            map_func(strip_doi),
        ],
        description="Optional. Format: e.g. 10.1234/foo.bar (one DOI per line).",
        placeholder="e.g. 10.1234/foo.bar (one DOI per line)...",
    )  # List identifier, rel type

    #
    # Journal
    #
    journal_title = fields.JournalField(description="Optional.")
    journal_volume = fields.TextField(label="Volume", description="Optional.")
    journal_issue = fields.TextField(label="Issue", description="Optional.")
    journal_pages = fields.TextField(label="Pages", description="Optional.")

    #
    # Book/report/chapter
    #
    partof_title = fields.TextField(label="Book title", description="Optional. "
        "Title of the book or report which this upload is part of.")
    partof_pages = fields.TextField(label="Pages", description="Optional.")

    imprint_isbn = fields.TextField(label="ISBN", description="Optional.",
        #placeholder="e.g 0-06-251587-X"
    )
    imprint_publisher = fields.TextField(label="Publisher", description="Optional.")
    imprint_place = fields.TextField(label="Place", description="Optional.",
        #placeholder="e.g city, country..."
    )

    #
    # Thesis
    #
    thesis_supervisors = fields.AuthorField(
        label="Supervisors",
        validators=[validators.optional()],
        description="Optional. Format: Family name, First name: Affiliation"
            " (one supervisor per line)",
        placeholder="Family name, First name: Affiliation (one supervisor per line)",
    )
    thesis_university = fields.TextField(
        description="Optional.",
        label='Awarding University',
        validators=[validators.optional()],
    )
    thesis_university._icon_html = '<i class="icon-building"></i>',

    #
    # Conference
    #
    conference_title = fields.TextField(description="Optional.")
    conference_acronym = fields.TextField(label="Acronym", description="Optional.")
    conference_dates = fields.TextField(label="Dates", description="Optional.",
        placeholder="e.g 21-22 November 2012..."
    )
    conference_place = fields.TextField(label="Place", description="Optional.",
        placeholder="e.g city, country..."
    )
    conference_url = fields.TextField(label="Website", description="Optional.")

    plupload_file = fields.FileUploadField(label="", widget=plupload_widget)

    #
    # Form configuration
    #
    _title = _('New upload')
    _drafting = True   # enable and disable drafting

    #
    # Grouping of fields
    #
    groups = [
        ('Type of file(s)',
            ['upload_type', 'publication_type', 'image_type',],
            {'indication': 'required'}),
        ('Basic information', [
            'doi', 'prereserve_doi', 'publication_date', 'title',  'creators', 'description',
            'keywords', 'notes',
        ], {'indication': 'required', }),
        ('License', [
            'access_right', 'embargo_date', 'license',
        ], {
            'indication': 'required',
            'description': 'Unless you explicitly specify the license conditions below for Open Access and Embargoed Access uploads,'
                ' you agree to release your data files under the terms of the Creative Commons Zero (CC0) waiver.'
                ' All authors of the data and publications have agreed to the terms of this waiver and license.' % {'site_name': CFG_SITE_NAME}
        }),
        ('Communities', [
            'collections',
        ], {
            'indication': 'recommended',
            'description': Markup('Any user can create a community collection on %(CFG_SITE_NAME)s (<a href="/communities/">browse communities</a>). Specify communities which you wish your upload to appear in. The owner of the community will be notified, and can either accept or reject your request.' % {'CFG_SITE_NAME': CFG_SITE_NAME})
        }),
        ('Funding', [
            'funding_source',
        ], {
            'indication': 'recommended',
            'description': '%s is integrated into reporting lines for research funded by the European Commission via OpenAIRE (http://www.openaire.eu). Specify grants which have funded your research, and we will let your funding agency know!' % CFG_SITE_NAME,
        }),
        ('Related datasets/publications', [
            'related_identifiers',
        ], {
            'classes': '',
            'indication': 'recommended',
            'description': 'Specify the Digital Object Identifiers (DOIs) of e.g. datasets referenced by your upload or e.g. publications referencing your upload:'
        }),
        ('Journal', [
            'journal_title', 'journal_volume', 'journal_issue',
            'journal_pages',
        ], {
            'classes': '',
            'indication': 'optional',
        }),
        ('Conference', [
            'conference_title', 'conference_acronym', 'conference_dates',
            'conference_place', 'conference_url',
        ], {
            'classes': '',
            'indication': 'optional',
        }),
        ('Book/Report/Chapter', [
            'imprint_publisher',  'imprint_place', 'imprint_isbn',
            'partof_title', 'partof_pages',
        ], {'classes': '', 'indication': 'optional', }),
        ('Thesis', [
            'thesis_university', 'thesis_supervisors',
        ], {
            'classes': '',
            'indication': 'optional',
        }),
    ]



