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

from __future__ import absolute_import

import json
from datetime import date
from jinja2 import Markup
from flask import request
from wtforms import validators, widgets
from wtforms.validators import ValidationError

from invenio.config import CFG_SITE_NAME, CFG_SITE_SUPPORT_EMAIL
from invenio.config import CFG_DATACITE_DOI_PREFIX

from invenio.base.i18n import _
from invenio.modules.knowledge.api import get_kb_mapping
from invenio.modules.deposit.form import WebDepositForm
from invenio.modules.deposit.field_widgets import date_widget, \
    plupload_widget, ButtonWidget, ExtendedListWidget, ListItemWidget, \
    TagListWidget, TagInput, ItemWidget, CKEditorWidget
from invenio.modules.deposit.filter_utils import strip_string, sanitize_html
from invenio.modules.deposit.validation_utils import doi_syntax_validator, \
    invalid_doi_prefix_validator, pre_reserved_doi_validator, required_if, \
    list_length, not_required_if, pid_validator, minted_doi_validator, \
    unchangeable
from invenio.modules.deposit.processor_utils import datacite_lookup, \
    PidSchemeDetection, PidNormalize, replace_field_data
from invenio.modules.deposit.autocomplete_utils import kb_autocomplete
from ...legacy.utils.zenodoutils import create_doi, filter_empty_helper

from .autocomplete import community_autocomplete
from .validators import community_validator
from . import fields as zfields


from invenio.modules.deposit import fields


__all__ = ['ZenodoForm']


#
# Local processors
#
local_datacite_lookup = datacite_lookup(mapping=dict(
    get_titles='title',
    get_dates='publication_date',
    get_description='description',
))


#
# Local autocomplete mappers
#
def map_result(func, mapper):
    def inner(form, field, term, limit=50):
        prefix = form._prefix
        return map(
            lambda x: mapper(x, prefix),
            func(form, field, term, limit=limit)
        )
    return inner


def communityform_mapper(obj, prefix):
    obj.update({
        'fields': {
            '%sidentifier' % prefix: obj['id'],
            '%stitle' % prefix: obj['value'],
        }
    })
    return obj


def community_obj_value(key_name):
    from invenio.modules.communities.models import Community

    def _getter(field):
        if field.data:
            obj = Community.query.filter_by(id=field.data).first()
            if obj:
                return getattr(obj, key_name)
        return None
    return _getter


def authorform_mapper(obj, prefix):
    obj.update({
        'value': "%s: %s" % (obj['name'], obj['affiliation']),
        'fields': {
            '%sname' % prefix: obj['name'],
            '%saffiliation' % prefix: obj['affiliation'],
        }
    })
    return obj


def json_projects_kb_mapper(val):
    data = json.loads(val['value'])
    grant_id = data.get('grant_agreement_number', '')
    acronym = data.get('acronym', '')
    title = data.get('title', '')
    return {
        'value': "%s - %s (%s)" % (acronym, title, grant_id),
        'fields': {
            'id': grant_id,
            'acronym': acronym,
            'title': title,
        }
    }


def dummy_autocomplete(form, field, term, limit=50):
    return [
        {
            'name': 'Nielsen, Lars',
            'affiliation': 'CERN',
        },
        {
            'name': 'Mele, Salvatore',
            'affiliation': 'CERN',
        }
    ]


def grants_validator(form, field):
    if field.data:
        for item in field.data:
            val = get_kb_mapping('json_projects', str(item['id']))
            if val:
                data = json_projects_kb_mapper(val)
                item['acronym'] = data['fields']['acronym']
                item['title'] = data['fields']['title']
                continue
            raise ValidationError("Invalid grant identifier %s" % item['id'])


def grant_kb_value(key_name):
    def _getter(field):
        if field.data:
            val = get_kb_mapping('json_projects', str(field.data))
            if val:
                data = json_projects_kb_mapper(val)
                return data['fields'][key_name]
        return ''
    return _getter


#
# Subforms
#
class RelatedIdentifierForm(WebDepositForm):
    scheme = fields.TextField(
        label="",
        default='',
        widget_classes='span1',
        widget=widgets.HiddenInput(),
    )
    identifier = fields.TextField(
        label="",
        placeholder="e.g. 10.1234/foo.bar...",
        validators=[
            validators.optional(),
            pid_validator(),
        ],
        processors=[
            PidSchemeDetection(set_field='scheme'),
            PidNormalize(scheme_field='scheme'),
        ],
        widget_classes='span3',
    )
    relation = fields.SelectField(
        label="",
        choices=[
            ('isCitedBy', 'cites this upload'),
            ('cites', 'is cited by this upload'),
            ('isSupplementTo', 'is supplemented by this upload'),
            ('isSupplementedBy', 'is a supplement to this upload'),
            #('isPartof','upload is part of),
            #('hasPart','has part'),
        ],
        default='isSupplementTo',
        widget_classes='span2',
    )

    def validate_scheme(form, field):
        """
        Always set scheme based on value in identifier
        """
        from invenio.utils import persistentid
        schemes = persistentid.detect_identifier_schemes(
            form.data.get('identifier') or ''
        )
        if schemes:
            field.data = schemes[0]
        else:
            field.data = ''


class CreatorForm(WebDepositForm):
    name = fields.TextField(
        placeholder="Family name, First name",
        widget_classes='span3',
        #autocomplete=map_result(
        #    dummy_autocomplete,
        #    authorform_mapper
        #),
        validators=[
            required_if(
                'affiliation',
                [lambda x: bool(x.strip()), ],  # non-empty
                message="Creator name is required if you specify affiliation."
            ),
        ],
    )
    affiliation = fields.TextField(
        placeholder="Affiliation",
        widget_classes='span2',
    )


class CommunityForm(WebDepositForm):
    identifier = fields.TextField(
        widget=widgets.HiddenInput(),
        processors=[
            replace_field_data('title', community_obj_value('title')),
        ],
    )
    title = fields.TextField(
        placeholder="Start typing a community name...",
        autocomplete=map_result(
            community_autocomplete,
            communityform_mapper
        ),
        widget=TagInput(),
        widget_classes='span5',
    )
    provisional = fields.BooleanField(
        default=True,
        widget=widgets.HiddenInput(),
        processors=[
            replace_field_data('provisional', lambda x: x.object_data),
        ]
    )


class GrantForm(WebDepositForm):
    id = fields.TextField(
        widget=widgets.HiddenInput(),
        processors=[
            replace_field_data('acronym', grant_kb_value('acronym')),
            replace_field_data('title', grant_kb_value('title'))
        ],
    )
    acronym = fields.TextField(
        widget=widgets.HiddenInput(),
    )
    title = fields.TextField(
        placeholder="Start typing a grant number, name or abbreviation...",
        autocomplete=kb_autocomplete(
            'json_projects',
            mapper=json_projects_kb_mapper
        ),
        widget=TagInput(),
        widget_classes='span5',
    )


#
# Form
#
class ZenodoForm(WebDepositForm):
    #
    # Fields
    #
    upload_type = zfields.UploadTypeField(
        validators=[validators.required()],
        export_key='upload_type.type',
    )
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
            required_if('upload_type', ['publication']),
            validators.optional()
        ],
        hidden=True,
        disabled=True,
        export_key='upload_type.subtype',
    )
    image_type = fields.SelectField(
        choices=[
            ('figure', 'Figure'),
            ('plot', 'Plot'),
            ('drawing', 'Drawing'),
            ('diagram', 'Diagram'),
            ('photo', 'Photo'),
            ('other', 'Other'),
        ],
        validators=[
            required_if('upload_type', ['image']),
            validators.optional()
        ],
        hidden=True,
        disabled=True,
        export_key='upload_type.subtype',
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
        placeholder="e.g. 10.1234/foo.bar...",
        validators=[
            doi_syntax_validator,
            pre_reserved_doi_validator(
                'prereserve_doi',
                prefix=CFG_DATACITE_DOI_PREFIX
            ),
            invalid_doi_prefix_validator(prefix=CFG_DATACITE_DOI_PREFIX),
        ],
        processors=[
            local_datacite_lookup
        ],
        export_key='doi',
    )
    prereserve_doi = zfields.ReserveDOIField(
        label="",
        doi_field="doi",
        doi_creator=create_doi,
        widget=ButtonWidget(
            label=_("Pre-reserve DOI"),
            icon='icon-barcode',
            tooltip=_(
                'Pre-reserve a Digital Object Identifier for your upload. This'
                ' allows you know the DOI before you submit your upload, and'
                ' can thus include it in e.g. publications. The DOI is not'
                ' finally registered until submit your upload.'
            ),
        ),
    )
    publication_date = fields.Date(
        label=_('Publication date'),
        icon='icon-calendar',
        description='Required. Format: YYYY-MM-DD. The date your upload was '
        'made available in case it was already published elsewhere.',
        default=date.today(),
        validators=[validators.required()],
        widget=date_widget,
        widget_classes='input-sm col-md-3',
    )
    title = fields.TitleField(
        validators=[validators.required()],
        description='Required.',
        filters=[
            strip_string,
        ],
        export_key='title',
    )
    creators = fields.DynamicFieldList(
        fields.FormField(
            CreatorForm,
            widget=ExtendedListWidget(
                item_widget=ListItemWidget(with_label=False),
                class_='inline',
            ),
        ),
        label='Authors',
        add_label='Add another author',
        icon='icon-user',
        widget_classes='',
        min_entries=1,
        export_key='authors',
        validators=[validators.required(), list_length(
            min_num=1, element_filter=filter_empty_helper(),
        )],
    )
    description = fields.TextAreaField(
        label="Description",
        description='Required.',
        default='',
        icon='icon-pencil',
        validators=[validators.required(), ],
        widget=CKEditorWidget(
            toolbar=[
                ['PasteText', 'PasteFromWord'],
                ['Bold', 'Italic', 'Strike', '-',
                    'Subscript', 'Superscript', ],
                ['NumberedList', 'BulletedList'],
                ['Undo', 'Redo', '-', 'Find', 'Replace', '-', 'RemoveFormat'],
                ['SpecialChar', 'ScientificChar'], ['Source'], ['Maximize'],
            ],
            disableNativeSpellChecker=False,
            extraPlugins='scientificchar',
            removePlugins='elementspath',
        ),
        filters=[
            sanitize_html,
            strip_string,
        ],
    )
    keywords = fields.DynamicFieldList(
        fields.TextField(
            widget_classes="span5"
        ),
        label='Keywords',
        add_label='Add another keyword',
        icon='icon-tags',
        widget_classes='',
        min_entries=1,
    )
    notes = fields.TextAreaField(
        label="Additional notes",
        description='Optional.',
        default='',
        validators=[validators.optional()],
        filters=[
            strip_string,
        ],
        widget_classes='form-control',
    )

    #
    # Access rights
    #
    access_right = zfields.AccessRightField(
        label="Access right",
        description="Required. Open access uploads have considerably higher "
        "visibility on %s." % CFG_SITE_NAME,
        default="open",
        validators=[validators.required()]
    )
    embargo_date = fields.Date(
        label=_('Embargo date'),
        icon='icon-calendar',
        description='Required only for Embargoed Access uploads. Format: '
        'YYYY-MM-DD. The date your upload will be made publicly available '
        'in case it is under an embargo period from your publisher.',
        default=date.today(),
        validators=[
            required_if('access_right', ['embargoed']),
            validators.optional()
        ],
        widget=date_widget,
        widget_classes='input-small',
        hidden=True,
        disabled=True,
    )
    license = zfields.LicenseField(
        validators=[
            required_if('access_right', ['embargoed', 'open', ]),
            validators.required()
        ],
        default='cc-zero',
        domain_data=True,
        domain_content=True,
        domain_software=True,
        description='Required. The selected license applies to all of your '
        'files displayed in the bottom of the form. If you want to upload '
        'some files under a different license, please do so in two separate'
        ' uploads. If you think a license missing is in the list, please '
        'inform us at %s.' % CFG_SITE_SUPPORT_EMAIL,
        filters=[
            strip_string,
        ],
        placeholder="Start typing a license name or abbreviation...",
    )

    #
    # Collection
    #
    communities = fields.DynamicFieldList(
        fields.FormField(
            CommunityForm,
            widget=ExtendedListWidget(html_tag=None, item_widget=ItemWidget())
        ),
        validators=[community_validator],
        widget=TagListWidget(template="{{title}}"),
        icon='icon-group',
        export_key='provisional_communities',
    )

    #
    # Funding
    #
    grants = fields.DynamicFieldList(
        fields.FormField(
            GrantForm,
            widget=ExtendedListWidget(html_tag=None, item_widget=ItemWidget()),
            export_key=lambda f: {
                'identifier': f.data['id'],
                'title': "%s - %s (%s)" % (
                    f.data['acronym'], f.data['title'], f.data['id']
                )
            }
        ),
        widget=TagListWidget(template="{{acronym}} - {{title}} ({{id}})"),
        icon='icon-group',
        description="Optional. Note, a human %s curator will validate your"
                    " upload before reporting it to OpenAIRE, and you may "
                    "thus experience a delay before your upload is available "
                    "in OpenAIRE." % CFG_SITE_NAME,
        validators=[grants_validator],
    )

    #
    # Related work
    #
    related_identifiers = fields.DynamicFieldList(
        fields.FormField(
            RelatedIdentifierForm,
            description="Optional. Format: e.g. 10.1234/foo.bar",
            widget=ExtendedListWidget(
                item_widget=ListItemWidget(
                    with_label=False,
                ),
                class_='inline',
            ),
        ),
        label="Related identifiers",
        add_label='Add another related identifier',
        icon='icon-barcode',
        widget_classes='',
        min_entries=1,
    )

    #
    # Journal
    #
    journal_title = fields.TextField(
        label="Journal title",
        description="Optional.",
        validators=[
            required_if(
                'journal_volume', [lambda x: bool(x.strip()), ],  # non-empty
                message="Journal title is required if you specify either "
                        "volume, issue or pages."
            ),
            required_if(
                'journal_issue', [lambda x: bool(x.strip()), ],  # non-empty
                message="Journal title is required if you specify either "
                        "volume, issue or pages."
            ),
            required_if(
                'journal_pages', [lambda x: bool(x.strip()), ],  # non-empty
                message="Journal title is required if you specify either "
                        "volume, issue or pages."
            ),
        ],
        export_key='journal.title',
    )
    journal_volume = fields.TextField(
        label="Volume", description="Optional.", export_key='journal.volume',
    )
    journal_issue = fields.TextField(
        label="Issue", description="Optional.", export_key='journal.issue',
    )
    journal_pages = fields.TextField(
        label="Pages", description="Optional.", export_key='journal.pages',
    )

    #
    # Book/report/chapter
    #
    partof_title = fields.TextField(
        label="Book title",
        description="Optional. "
                    "Title of the book or report which this "
                    "upload is part of.",
        export_key='part_of.title',
    )
    partof_pages = fields.TextField(
        label="Pages",
        description="Optional.",
        export_key='part_of.pages',
    )

    imprint_isbn = fields.TextField(
        label="ISBN",
        description="Optional.",
        placeholder="e.g 0-06-251587-X",
        export_key='isbn',
    )
    imprint_publisher = fields.TextField(
        label="Publisher",
        description="Optional.",
        export_key='imprint.publisher',
    )
    imprint_place = fields.TextField(
        label="Place",
        description="Optional.",
        placeholder="e.g city, country...",
        export_key='imprint.place',
    )

    #
    # Thesis
    #
    thesis_supervisors = fields.DynamicFieldList(
        fields.FormField(
            CreatorForm,
            widget=ExtendedListWidget(
                item_widget=ListItemWidget(with_label=False),
                class_='inline',
            ),
        ),
        label='Supervisors',
        add_label='Add another supervisor',
        icon='icon-user',
        widget_classes='',
        min_entries=1,
    )
    thesis_university = fields.TextField(
        description="Optional.",
        label='Awarding University',
        validators=[validators.optional()],
        icon='icon-building',
    )

    #
    # Conference
    #
    conference_title = fields.TextField(
        label="Conference title",
        description="Optional.",
        validators=[
            not_required_if('conference_acronym', [lambda x: bool(x.strip())]),
            required_if(
                'conference_dates', [lambda x: bool(x.strip()), ],  # non-empty
                message="Conference title or acronym is required if you "
                        "specify either dates or place."
            ),
            required_if(
                'conference_place', [lambda x: bool(x.strip()), ],  # non-empty
                message="Conference title or acronym is required if you "
                        "specify either dates or place."
            ),
        ],
        export_key="meetings.title"
    )
    conference_acronym = fields.TextField(
        label="Acronym",
        description="Optional.",
        validators=[
            not_required_if('conference_title', [lambda x: bool(x.strip())]),
            required_if(
                'conference_dates', [lambda x: bool(x.strip()), ],  # non-empty
                message="Conference title or acronym is required if you "
                        "specify either dates or place."
            ),
            required_if(
                'conference_place', [lambda x: bool(x.strip()), ],  # non-empty
                message="Conference title or acronym is required if you "
                        "specify either dates or place."
            ),
        ],
        export_key="meetings.acronym",
    )
    conference_dates = fields.TextField(
        label="Dates", description="Optional.",
        placeholder="e.g 21-22 November 2012...",
        export_key="meetings.dates",
    )
    conference_place = fields.TextField(
        label="Place",
        description="Optional.",
        placeholder="e.g city, country...",
        export_key="meetings.place",
    )
    conference_url = fields.TextField(
        label="Website",
        description="Optional. E.g. http://zenodo.org",
        validators=[validators.optional(), validators.URL()]
    )

    #
    # File upload field
    #
    plupload_file = fields.FileUploadField(
        label="",
        widget=plupload_widget,
        export_key=False
    )

    def validate_plupload_file(form, field):
        """ Ensure minimum one file is attached. """
        if not getattr(request, 'is_api_request', False):
            # Tested in API by a separate workflow task.
            if len(form.files) == 0:
                raise ValidationError("You must provide minimum one file.")


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
            ['upload_type', 'publication_type', 'image_type', ],
            {'indication': 'required'}),
        ('Basic information', [
            'doi', 'prereserve_doi', 'publication_date', 'title',  'creators', 'description',
            'keywords', 'notes',
        ], {'indication': 'required', }),
        ('License', [
            'access_right', 'embargo_date', 'license',
        ], {
            'indication': 'required',
            #'description': 'Unless you explicitly specify the license conditions below for Open Access and Embargoed Access uploads,'
            #' you agree to release your data files under the terms of the Creative Commons Zero (CC0) waiver.'
            #' All authors of the data and publications have agreed to the terms of this waiver and license.'
        }),
        ('Communities', [
            'communities',
        ], {
            'indication': 'recommended',
            'description': Markup('Any user can create a community collection on %(CFG_SITE_NAME)s (<a href="/communities/">browse communities</a>). Specify communities which you wish your upload to appear in. The owner of the community will be notified, and can either accept or reject your request.' % {'CFG_SITE_NAME': CFG_SITE_NAME})
        }),
        ('Funding', [
            'grants',
        ], {
            'indication': 'recommended',
            'description': '%s is integrated into reporting lines for research funded by the European Commission via OpenAIRE (http://www.openaire.eu). Specify grants which have funded your research, and we will let your funding agency know!' % CFG_SITE_NAME,
        }),
        ('Related datasets/publications', [
            'related_identifiers',
        ], {
            'classes': '',
            'indication': 'recommended',
            'description': 'Specify identifiers of related publications and datasets. Supported identifiers include: DOI, Handle, ARK, PURL, ISSN, ISBN, PubMed ID, PubMed Central ID, ADS Bibliographic Code, arXiv, Life Science Identifiers (LSID), EAN-13, ISTC, URNs and URLs.'
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
            'imprint_publisher',  'imprint_place', 'imprint_isbn', '-',
            'partof_title', 'partof_pages',
        ], {'classes': '', 'indication': 'optional', }),
        ('Thesis', [
            'thesis_university', 'thesis_supervisors',
        ], {
            'classes': '',
            'indication': 'optional',
        }),
    ]


def filter_fields(groups):
    def _inner(element):
        element = list(element)
        element[1] = filter(lambda x: x in groups, element[1])
        return tuple(element)
    return _inner


class EditFormMixin(object):
    """
    Mixin class for forms that needs editing.
    """
    recid = fields.IntegerField(
        validators=[
            unchangeable(),
        ],
        widget=widgets.HiddenInput(),
        label=""
    )
    version_id = fields.DateTimeField(
        validators=[
            unchangeable(),
        ],
        widget=widgets.HiddenInput(),
        label=""
    )


class ZenodoEditForm(ZenodoForm, EditFormMixin):
    """
    Specialized form for editing a record
    """
    # Remove some fields.
    doi = fields.DOIField(
        label="Digital Object Identifier",
        description="Optional. Did your publisher already assign a DOI to your"
        " upload? If not, leave the field empty and we will register a new"
        " DOI for you. A DOI allow others to easily and unambiguously cite"
        " your upload.",
        placeholder="e.g. 10.1234/foo.bar...",
        validators=[
            doi_syntax_validator,
            minted_doi_validator(prefix=CFG_DATACITE_DOI_PREFIX),
            invalid_doi_prefix_validator(prefix=CFG_DATACITE_DOI_PREFIX),
        ],
        processors=[
            local_datacite_lookup
        ],
        export_key='doi',
    )
    prereserve_doi = None
    plupload_file = None

    _title = _('Edit upload')
    template = "webdeposit_edit.html"
