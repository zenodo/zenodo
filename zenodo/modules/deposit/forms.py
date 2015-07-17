# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2012, 2013, 2014, 2015 CERN.
#
# Zenodo is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import

import json
from datetime import date

from flask import request

from invenio.base.i18n import _
from invenio.config import CFG_DATACITE_DOI_PREFIX
from invenio.config import CFG_SITE_NAME, CFG_SITE_SUPPORT_EMAIL
from invenio.modules.deposit import fields
from invenio.modules.deposit.autocomplete_utils import kb_autocomplete
from invenio.modules.deposit.field_widgets import ButtonWidget, \
    CKEditorWidget, ColumnInput, ExtendedListWidget, ItemWidget, TagInput, \
    TagListWidget, date_widget, plupload_widget
from invenio.modules.deposit.filter_utils import sanitize_html, strip_string
from invenio.modules.deposit.form import WebDepositForm
from invenio.modules.deposit.processor_utils import PidNormalize, \
    PidSchemeDetection, datacite_lookup, replace_field_data
from invenio.modules.deposit.validation_utils import DOISyntaxValidator, \
    invalid_doi_prefix_validator, list_length, minted_doi_validator, \
    not_required_if, pid_validator, pre_reserved_doi_validator, required_if, \
    unchangeable
from invenio.modules.knowledge.api import get_kb_mapping
from invenio.utils.html import CFG_HTML_BUFFER_ALLOWED_TAG_WHITELIST

from jinja2 import Markup

from wtforms import validators, widgets
from wtforms.validators import ValidationError

from . import fields as zfields
from .autocomplete import community_autocomplete
from .validators import community_validator
from ...legacy.utils.zenodoutils import create_doi, filter_empty_helper


__all__ = ('ZenodoForm', )


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
    scheme = fields.StringField(
        label="",
        default='',
        widget_classes='',
        widget=widgets.HiddenInput(),
    )
    identifier = fields.StringField(
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
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-4"),
    )
    relation = fields.SelectField(
        label="",
        choices=[
            ('isCitedBy', 'cites this upload'),
            ('cites', 'is cited by this upload'),
            ('isSupplementTo', 'is supplemented by this upload'),
            ('isSupplementedBy', 'is a supplement to this upload'),
            ('isNewVersionOf', 'is previous version of this upload'),
            ('isPreviousVersionOf', 'is new version of this upload'),
            ('isPartOf', 'has this upload as part'),
            ('hasPart', 'is part of this upload'),
            ('isIdenticalTo', 'is identical to upload'),
            ('isAlternativeIdentifier', 'is alternate identifier'),
        ],
        default='isSupplementTo',
        widget_classes='form-control',
        widget=ColumnInput(
            class_="col-xs-6 col-pad-0", widget=widgets.Select()
        ),
    )

    def validate_scheme(form, field):
        """Set scheme based on value in identifier."""
        from invenio.utils import persistentid
        schemes = persistentid.detect_identifier_schemes(
            form.data.get('identifier') or ''
        )
        if schemes:
            field.data = schemes[0]
        else:
            field.data = ''


class CreatorForm(WebDepositForm):
    name = fields.StringField(
        placeholder="Family name, First name",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-6"),
        validators=[
            required_if(
                'affiliation',
                [lambda x: bool(x.strip()), ],  # non-empty
                message="Creator name is required if you specify affiliation."
            ),
        ],
    )
    affiliation = fields.StringField(
        placeholder="Affiliation",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-4 col-pad-0"),
    )
    orcid = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            PidNormalize(scheme='orcid'),
        ],
    )
    gnd = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            PidNormalize(scheme='gnd'),
        ],
    )

    def validate_orcid(form, field):
        if field.data:
            from invenio.utils import persistentid
            schemes = persistentid.detect_identifier_schemes(
                field.data or ''
            )
            if 'orcid' not in schemes:
                raise ValidationError("Not a valid ORCID-identifier.")

    def validate_gnd(form, field):
        if field.data:
            from invenio.utils import persistentid
            schemes = persistentid.detect_identifier_schemes(
                field.data or ''
            )
            if 'gnd' not in schemes:
                raise ValidationError("Not a valid GND-identifier.")


class ContributorsForm(WebDepositForm):
    name = fields.StringField(
        placeholder="Family name, First name",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-4 col-pad-0"),
        validators=[
            required_if(
                'affiliation',
                [lambda x: bool(x.strip()), ],  # non-empty
                message="Contributor name is required if you specify affiliation."
            ),
        ],
    )
    affiliation = fields.StringField(
        placeholder="Affiliation",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-3 col-pad-0"),
    )
    type = fields.SelectField(
        label="",
        choices=[
            ('prc', 'Contact person'),
            ('col', 'Data collector'),
            ('cur', 'Data curator'),
            ('dtm', 'Data manager'),
            ('edt', 'Editor'),
            ('res', 'Researcher'),
            ('cph', 'Rights holder'),
            ('spn', 'Sponsor'),
            ('oth', 'Other'),
        ],
        default='cur',
        widget_classes='form-control',
        widget=ColumnInput(
            class_="col-xs-3 col-pad-0", widget=widgets.Select()
        ),
    )
    orcid = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            PidNormalize(scheme='orcid'),
        ],
    )
    gnd = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            PidNormalize(scheme='gnd'),
        ],
    )

    def validate_orcid(form, field):
        if field.data:
            from invenio.utils import persistentid
            schemes = persistentid.detect_identifier_schemes(
                field.data or ''
            )
            if 'orcid' not in schemes:
                raise ValidationError("Not a valid ORCID-identifier.")

    def validate_gnd(form, field):
        if field.data:
            from invenio.utils import persistentid
            schemes = persistentid.detect_identifier_schemes(
                field.data or ''
            )
            if 'gnd' not in schemes:
                raise ValidationError("Not a valid GND-identifier.")


class SubjectsForm(WebDepositForm):
    term = fields.StringField(
        placeholder="Term",
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-5"),
        validators=[
            required_if(
                'identifier',
                [lambda x: bool(x.strip()), ],  # non-empty
                message="Term is required if you specify identifier."
            ),
        ],
    )
    scheme = fields.StringField(
        label="",
        default='',
        widget_classes='',
        widget=widgets.HiddenInput(),
    )
    identifier = fields.StringField(
        label="",
        placeholder="Identifier",
        validators=[
            validators.optional(),
            pid_validator(),
        ],
        processors=[
            PidSchemeDetection(set_field='scheme'),
            PidNormalize(scheme_field='scheme'),
        ],
        widget_classes='form-control',
        widget=ColumnInput(class_="col-xs-5 col-pad-0"),
    )

    def validate_scheme(form, field):
        """Set scheme based on value in identifier."""
        from invenio.utils import persistentid
        schemes = persistentid.detect_identifier_schemes(
            form.data.get('identifier') or ''
        )
        if schemes:
            field.data = schemes[0]
        else:
            field.data = ''


class CommunityForm(WebDepositForm):
    identifier = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            replace_field_data('title', community_obj_value('title')),
        ],
    )
    title = fields.StringField(
        placeholder="Start typing a community name...",
        autocomplete_fn=community_autocomplete,
        widget=TagInput(),
        widget_classes='form-control',
    )
    provisional = fields.BooleanField(
        default=True,
        widget=widgets.HiddenInput(),
        processors=[
            replace_field_data('provisional', lambda x: x.object_data),
        ]
    )


class GrantForm(WebDepositForm):
    id = fields.StringField(
        widget=widgets.HiddenInput(),
        processors=[
            replace_field_data('acronym', grant_kb_value('acronym')),
            replace_field_data('title', grant_kb_value('title'))
        ],
    )
    acronym = fields.StringField(
        widget=widgets.HiddenInput(),
    )
    title = fields.StringField(
        placeholder="Start typing a grant number, name or abbreviation...",
        autocomplete_fn=kb_autocomplete(
            'json_projects',
            mapper=json_projects_kb_mapper
        ),
        widget=TagInput(),
        widget_classes='form-control',
    )


#
# Form
#
class ZenodoForm(WebDepositForm):

    """Zenodo Upload Form."""

    #
    # Fields
    #
    upload_type = zfields.UploadTypeField(
        validators=[validators.DataRequired()],
        export_key='upload_type.type',
    )
    publication_type = fields.SelectField(
        label='Publication Type',
        choices=[
            ('book', 'Book'),
            ('section', 'Book section'),
            ('conferencepaper', 'Conference paper'),
            ('article', 'Journal article'),
            ('patent', 'Patent'),
            ('preprint', 'Preprint'),
            ('deliverable', _('Project Deliverable')),
            ('milestone', _('Project Milestone')),
            ('proposal', 'Proposal'),
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
        " DOI for you. A DOI allows others to easily and unambiguously cite"
        " your upload.",
        placeholder="e.g. 10.1234/foo.bar...",
        validators=[
            DOISyntaxValidator(),
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
        icon='fa fa-barcode fa-fw',
    )
    prereserve_doi = zfields.ReserveDOIField(
        label="",
        doi_field="doi",
        doi_creator=create_doi,
        widget=ButtonWidget(
            label=_("Pre-reserve DOI"),
            icon='fa fa-barcode',
            tooltip=_(
                'Pre-reserve a Digital Object Identifier for your upload. This'
                ' allows you to know the DOI before you submit your upload, '
                'and can thus include it in e.g. publications. The DOI is not'
                ' finally registered until submit your upload.'
            ),
        ),
    )
    publication_date = fields.Date(
        label=_('Publication date'),
        icon='fa fa-calendar fa-fw',
        description='Required. Format: YYYY-MM-DD. In case your upload '
        'was already published elsewhere, please use the date of first'
        ' publication.',
        default=date.today(),
        validators=[validators.DataRequired()],
        widget=date_widget,
        widget_classes='input-sm',
    )
    title = fields.TitleField(
        validators=[validators.DataRequired()],
        description='Required.',
        filters=[
            strip_string,
        ],
        export_key='title',
        icon='fa fa-book fa-fw',
    )
    creators = fields.DynamicFieldList(
        fields.FormField(
            CreatorForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div'
            ),
        ),
        label='Authors',
        add_label='Add another author',
        icon='fa fa-user fa-fw',
        widget_classes='',
        min_entries=1,
        export_key='authors',
        validators=[validators.DataRequired(), list_length(
            min_num=1, element_filter=filter_empty_helper(),
        )],
    )
    description = fields.TextAreaField(
        label="Description",
        description='Required.',
        default='',
        icon='fa fa-pencil fa-fw',
        validators=[validators.DataRequired(), ],
        widget=CKEditorWidget(
            toolbar=[
                ['PasteText', 'PasteFromWord'],
                ['Bold', 'Italic', 'Strike', '-',
                 'Subscript', 'Superscript', ],
                ['NumberedList', 'BulletedList', 'Blockquote'],
                ['Undo', 'Redo', '-', 'Find', 'Replace', '-', 'RemoveFormat'],
                ['Mathjax', 'SpecialChar', 'ScientificChar'], ['Source'],
                ['Maximize'],
            ],
            disableNativeSpellChecker=False,
            extraPlugins='scientificchar,mathjax,blockquote',
            removePlugins='elementspath',
            removeButtons='',
            # Must be set, otherwise MathJax tries to include MathJax via the
            # http on CDN instead of https.
            mathJaxLib='https://cdn.mathjax.org/mathjax/latest/MathJax.js?'
                       'config=TeX-AMS-MML_HTMLorMML'
        ),
        filters=[
            sanitize_html(allowed_tag_whitelist=(
                CFG_HTML_BUFFER_ALLOWED_TAG_WHITELIST + ('span',)
            )),
            strip_string,
        ],
    )
    keywords = fields.DynamicFieldList(
        fields.StringField(
            widget_classes='form-control',
            widget=ColumnInput(class_="col-xs-10"),
        ),
        label='Keywords',
        add_label='Add another keyword',
        icon='fa fa-tags fa-fw',
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
        icon='fa fa-pencil fa-fw',
    )

    #
    # Access rights
    #
    access_right = zfields.AccessRightField(
        label="Access right",
        description="Required. Open access uploads have considerably higher "
        "visibility on %s." % CFG_SITE_NAME,
        default="open",
        validators=[validators.DataRequired()]
    )
    embargo_date = fields.Date(
        label=_('Embargo date'),
        icon='fa fa-calendar fa-fw',
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
            validators.DataRequired()
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
        icon='fa fa-certificate fa-fw',
    )
    access_conditions = fields.TextAreaField(
        label=_('Conditions'),
        icon='fa fa-pencil fa-fw',
        description='Specify the conditions under which you grant users '
                    'access to the files in your upload. User requesting '
                    'access will be asked to justify how they fulfil the '
                    'conditions. Based on the justification, you decide '
                    'who to grant/deny access. You are not allowed to '
                    'charge users for granting access to data hosted on '
                    'Zenodo.',
        default="",
        validators=[
            required_if('access_right', ['restricted']),
            validators.optional()
        ],
        widget=CKEditorWidget(
            toolbar=[
                ['PasteText', 'PasteFromWord'],
                ['Bold', 'Italic', 'Strike', '-',
                 'Subscript', 'Superscript', ],
                ['NumberedList', 'BulletedList', 'Blockquote'],
                ['Undo', 'Redo', '-', 'Find', 'Replace', '-', 'RemoveFormat'],
                ['Mathjax', 'SpecialChar', 'ScientificChar'], ['Source'],
                ['Maximize'],
            ],
            disableNativeSpellChecker=False,
            extraPlugins='scientificchar,mathjax,blockquote',
            removePlugins='elementspath',
            removeButtons='',
            # Must be set, otherwise MathJax tries to include MathJax via the
            # http on CDN instead of https.
            mathJaxLib='https://cdn.mathjax.org/mathjax/latest/MathJax.js?'
                       'config=TeX-AMS-MML_HTMLorMML'
        ),
        filters=[
            sanitize_html(allowed_tag_whitelist=(
                CFG_HTML_BUFFER_ALLOWED_TAG_WHITELIST + ('span',)
            )),
            strip_string,
        ],
        hidden=True,
        disabled=True,
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
        widget_classes=' dynamic-field-list',
        icon='fa fa-group fa-fw',
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
        widget_classes=' dynamic-field-list',
        icon='fa fa-money fa-fw',
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
                item_widget=ItemWidget(),
                html_tag='div'
            ),
        ),
        label="Related identifiers",
        add_label='Add another related identifier',
        icon='fa fa-barcode fa-fw',
        widget_classes='',
        min_entries=1,
    )

    #
    # Subjects
    #
    subjects = fields.DynamicFieldList(
        fields.FormField(
            SubjectsForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div'
            ),
        ),
        label="Subjects",
        add_label='Add another subject',
        icon='fa fa-tags fa-fw',
        widget_classes='',
        min_entries=1,
    )

    #
    # Journal
    #
    journal_title = fields.StringField(
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
    journal_volume = fields.StringField(
        label="Volume", description="Optional.", export_key='journal.volume',
    )
    journal_issue = fields.StringField(
        label="Issue", description="Optional.", export_key='journal.issue',
    )
    journal_pages = fields.StringField(
        label="Pages", description="Optional.", export_key='journal.pages',
    )

    #
    # Book/report/chapter
    #
    partof_title = fields.StringField(
        label="Book title",
        description="Optional. "
                    "Title of the book or report which this "
                    "upload is part of.",
        export_key='part_of.title',
    )
    partof_pages = fields.StringField(
        label="Pages",
        description="Optional.",
        export_key='part_of.pages',
    )

    imprint_isbn = fields.StringField(
        label="ISBN",
        description="Optional.",
        placeholder="e.g 0-06-251587-X",
        export_key='isbn',
    )
    imprint_publisher = fields.StringField(
        label="Publisher",
        description="Optional.",
        export_key='imprint.publisher',
    )
    imprint_place = fields.StringField(
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
                item_widget=ItemWidget(),
                html_tag='div'
            ),
        ),
        label='Supervisors',
        add_label='Add another supervisor',
        icon='fa fa-user fa-fw',
        widget_classes='',
        min_entries=1,
    )
    thesis_university = fields.StringField(
        description="Optional.",
        label='Awarding University',
        validators=[validators.optional()],
        icon='fa fa-building fa-fw',
    )

    #
    # Contributors
    #
    contributors = fields.DynamicFieldList(
        fields.FormField(
            ContributorsForm,
            widget=ExtendedListWidget(
                item_widget=ItemWidget(),
                html_tag='div'
            ),
        ),
        label='Contributors',
        add_label='Add another contributor',
        icon='fa fa-users fa-fw',
        widget_classes='',
        min_entries=0,
    )

    #
    # Conference
    #
    conference_title = fields.StringField(
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
    conference_acronym = fields.StringField(
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
    conference_dates = fields.StringField(
        label="Dates", description="Optional.",
        placeholder="e.g 21-22 November 2012...",
        export_key="meetings.dates",
    )
    conference_place = fields.StringField(
        label="Place",
        description="Optional.",
        placeholder="e.g city, country...",
        export_key="meetings.place",
    )
    conference_url = fields.StringField(
        label="Website",
        description="Optional. E.g. http://zenodo.org",
        validators=[validators.optional(), validators.URL()]
    )
    conference_session = fields.StringField(
        label="Session",
        description="Optional. Number of session within the conference.",
        placeholder="e.g VI",
        export_key="meetings.session",
    )
    conference_session_part = fields.StringField(
        label="Part",
        description="Optional. Number of part within a session.",
        placeholder="e.g 1",
        export_key="meetings.session_part",
    )

    #
    # References
    #
    references = zfields.TextAreaListField(
        label="References",
        description="Optional. Format: One reference per line.",
        validators=[validators.optional(), ],
        icon='fa fa-bookmark',
        placeholder="One reference per line...",
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
        """Ensure minimum one file is attached."""
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
            'doi', 'prereserve_doi', 'publication_date', 'title',  'creators',
            'description', 'keywords', 'notes',
        ], {'indication': 'required', }),
        ('License', [
            'access_right', 'embargo_date', 'license', 'access_conditions'
        ], {
            'indication': 'required',
            # 'description': (
            #     'Unless you explicitly specify the license conditions below'
            #     ' for Open Access and Embargoed Access uploads, you agree to'
            #     ' release your data files under the terms of the Creative'
            #     ' Commons Zero (CC0) waiver. All authors of the data and'
            #     ' publications have agreed to the terms of this waiver and'
            #     ' license.')
        }),
        ('Communities', [
            'communities',
        ], {
            'indication': 'recommended',
            'description': Markup(
                'Any user can create a community collection on'
                ' %(CFG_SITE_NAME)s (<a href="/communities/">browse'
                ' communities</a>). Specify communities which you wish your'
                ' upload to appear in. The owner of the community will'
                ' be notified, and can either accept or reject your'
                ' request.' % {'CFG_SITE_NAME': CFG_SITE_NAME}),
        }),
        ('Funding', [
            'grants',
        ], {
            'indication': 'recommended',
            'description': (
                '%s is integrated into reporting lines for research funded'
                ' by the European Commission via OpenAIRE'
                ' (http://www.openaire.eu). Specify grants which have funded'
                ' your research, and we will let your funding agency'
                ' know!' % CFG_SITE_NAME
            ),
        }),
        ('Related/alternate identifiers', [
            'related_identifiers',
        ], {
            'classes': '',
            'indication': 'recommended',
            'description': (
                'Specify identifiers of related publications and datasets.'
                ' Supported identifiers include: DOI, Handle, ARK, PURL,'
                ' ISSN, ISBN, PubMed ID, PubMed Central ID, ADS Bibliographic'
                ' Code, arXiv, Life Science Identifiers (LSID), EAN-13, ISTC,'
                ' URNs and URLs.'
            ),
        }),
        ('References', [
            'references',
        ], {
            'classes': '',
            'indication': 'optional',
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
            'conference_place', 'conference_url', '-', 'conference_session',
            'conference_session_part'
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
        ('Subjects', [
            'subjects'
        ], {
            'classes': '',
            'indication': 'optional',
            'description': 'Thsi field contains a topical subject used as a subject added entry.',
        }),
        ('Contributors', [
            'contributors'
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

    """Mixin class for forms that needs editing."""

    recid = fields.IntegerField(
        validators=[
            unchangeable(),
        ],
        widget=widgets.HiddenInput(),
        label=""
    )
    modification_date = fields.DateTimeField(
        validators=[
            unchangeable(),
        ],
        widget=widgets.HiddenInput(),
        label="",
    )


class ZenodoEditForm(ZenodoForm, EditFormMixin):

    """Specialized form for editing a record."""

    # Remove some fields.
    doi = fields.DOIField(
        label="Digital Object Identifier",
        description="Optional. Did your publisher already assign a DOI to your"
        " upload? If not, leave the field empty and we will register a new"
        " DOI for you. A DOI allow others to easily and unambiguously cite"
        " your upload.",
        placeholder="e.g. 10.1234/foo.bar...",
        validators=[
            DOISyntaxValidator(),
            minted_doi_validator(prefix=CFG_DATACITE_DOI_PREFIX),
            invalid_doi_prefix_validator(prefix=CFG_DATACITE_DOI_PREFIX),
        ],
        processors=[
            local_datacite_lookup
        ],
        export_key='doi',
        readonly="true"
    )
    prereserve_doi = None
    plupload_file = None

    _title = _('Edit upload')
    template = "deposit/edit.html"
