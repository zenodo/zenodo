"""WebAccount Forms"""

from invenio.webinterface_handler_flask_utils import _
from invenio.wtforms_utils import InvenioForm as Form
from flask.ext import wtf
from sqlalchemy.exc import SQLAlchemyError

from wtforms import SubmitField, Field, validators
from invenio.wtforms_utils import InvenioForm as Form
from invenio.webdeposit_field_widgets import bootstrap_submit
from invenio.webdeposit_load_fields import fields
from invenio.config import CFG_SITE_NAME, CFG_SITE_SUPPORT_EMAIL
from invenio import openaire_validators as oa_validators
from datetime import datetime, date
from werkzeug.datastructures import MultiDict

#
# Mapping forms to different objects
#
class FormMapperI(object):
    """
    Interface for mapping form data to another object
    """
    def __init__(self, obj):
        self.obj = obj

    def get_object(self):
        return self.obj

    def map(self, form):
        for field in form:
            self.map_field(form, field)
        return self.get_object()

    def map_field(self, form, field):
        func_name = "map_%s" % field.name
        try:
            map_func = getattr(self, func_name)
            if callable(map_func):
                map_func(form, field)
                return
        except AttributeError:
            pass

        self.set_value(field.name, field.data)

    def set_value(self, name, value):
        setattr(self.obj, name, value)


class DictFormMapper(FormMapperI):
    """
    Simple form mapper that simple creates a dictionary of form values
    """
    def __init__(self):
        self.obj = {}

    def set_value(self, name, value):
        self.obj[name] = value


class PublicationMapper(FormMapperI):
    """
    Map an OpenAIREPublication into a dictionary ready for form values.
    """
    def __init__(self):
        self.obj = MultiDict()

    def map(self, pub):
        metadata = pub.get_form_values()
        if metadata:
            for key, value in metadata.items():
                func_name = "map_%s" % key
                try:
                    map_func = getattr(self, func_name)
                    if callable(map_func):
                        map_func(metadata, key, value)
                except AttributeError:
                    pass
                self.set_value(key, value)
        return self.get_object()

    def set_value(self, key, value):
        if isinstance(value, str):
            value = value.decode('utf8')
        self.obj[key] = value

    def map_publication_date(self, metadata, key, value):
        self.to_date(key, value)

    def map_embargo_date(self, metadata, key, value):
        self.to_date(key, value)

    def to_date(self, key, value):
        try:
            if value and isinstance(value, basestring):
                if len(value) > 10:
                    value = value[:10]
                value = datetime.strptime(value, "%Y-%m-%d").date()
            else:
                value = ""
        except ValueError:
            value = ""
        self.set_value(key, value)


class DepositionFormMapper(FormMapperI):
    # exclude = ['publication_type', 'image_type']
    # key_mapping = {
    #     # One to one mapping
    #     # 'doi', 'publication_date', 'keywords', 'notes', 'embargo_date',
    #     # 'journal_title', 'title'
    #     # New one to one mapping:
    #     # 'license', 'conference_place', 'related_identifiers', 'partof_year'
    #     #-----------------'funding_source': '',
    #     # Old field
    #     # 'publication_type',
    #     # 'report_type',
    #     # 'thesis_type',
    #     # 'contribution_type',
    #     # 'related_publications',
    #     # 'related_datasets',
    #     # 'dataset_publisher',
    #     # 'meeting_town',
    #     # 'meeting_country',
    #     'creators': 'authors',
    #     'description': 'abstract',
    #     'journal_volume': 'volume',
    #     'journal_issue': 'issue',
    #     'journal_pages': 'pages',
    #     'partof_title': 'book_title',
    #     'partof_pages': 'book_pages',
    #     'imprint_isbn': 'isbn',
    #     'imprint_publisher': 'publisher',
    #     'imprint_place': 'place',
    #     'thesis_supervisors': 'supervisors',
    #     'thesis_university': 'university',
    #     'conference_title': 'meeting_title',
    #     'conference_acronym': 'meeting_acronym',
    #     'conference_dates': 'meeting_dates',
    #     'conference_url': 'meeting_url',
    # }
    # access_right_value_map = {
    #     'open': 'openAccess',
    #     'closed': 'closedAccess',
    #     'restricted': 'restrictedAccess',
    #     'embargoed': 'embargoedAccess',
    # }
    def __init__(self, obj):
        self.pub = obj
        super(DepositionFormMapper, self).__init__({})

    def get_object(self):
        self.pub.merge_form(self.obj)
        return self.pub

    def map_publication_date(self, form, field):
        self.set_to_string(field)

    def map_embargo_date(self, form, field):
        self.set_to_string(field)

    def set_value(self, name, value):
        if isinstance(value, unicode):
            value = value.encode('utf8')
        self.obj[name] = value

    def set_to_string(self, field):
        self.set_value(field.name, unicode(field.data).encode('utf8'))


#
# Filters
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
# Form
#
class DepositionForm(Form):
    """
    ZENODO deposition form
    """
    field_sets = [
        ('Type of file(s)', [
            'upload_type', 'publication_type', 'image_type',
        ], {'classes': 'in'}),
        ('Collections', [
            'collections',
        ], {
            'classes': 'in',
            'state': 'recommended',
        }),
        ('Basic information', [
            'doi', 'publication_date', 'title',  'creators', 'description',
            'keywords', 'notes',
        ], {'classes': 'in'}),
        ('License', [
            'access_right', 'embargo_date', 'license',
        ], {
            'classes': 'in',
            'state': 'required',
            'description': 'Unless you explicitly specify the license conditions below,'
                ' you agree to release your data under the terms of the Creative Commons Zero (CC0) waiver'
                ' and your publications under the terms of the Creative Commons Attribution 3.0 Unported (CC-BY)'
                ' license. All authors of the data and publications have agreed to the terms of this waiver and license.' % {'site_name': CFG_SITE_NAME}
        }),
        ('Funding', [
            'funding_source',
        ], {
            'classes': 'in',
            'state': 'recommended',
            'description': '%s is integrated into reporting lines for research funded by the European Commission via OpenAIRE (http://www.openaire.eu). Specify grants which have funded your research, and we will let your funding agency now!' % CFG_SITE_NAME,
        }),
        ('Related datasets/publications', [
            'related_identifiers',
        ], {
            'classes': '',
            'state': 'recommended',
            'description': 'Specify the Digital Object Identifiers (DOIs) of e.g. datasets referenced by your upload or e.g. publications referencing your upload:'
        }),
        ('Journal', [
            'journal_title', 'journal_volume', 'journal_issue',
            'journal_pages',
        ], {
            'classes': '',
            'state': 'optional',
        }),
        ('Conference', [
            'conference_title', 'conference_acronym', 'conference_dates',
            'conference_place', 'conference_url',
        ], {
            'classes': '',
            'state': 'optional',
        }),
        ('Book/Report/Chapter', [
            'imprint_publisher',  'imprint_place', 'imprint_isbn',
            '-', 'partof_title', 'partof_pages',
        ], {'classes': '', 'state': 'optional', }),
        ('Thesis', [
            'thesis_university', 'thesis_supervisors',
        ], {
            'classes': '',
            'state': 'optional',
        }),
    ]

    field_placeholders = {
        'doi': 'e.g. 10.1234/foo.bar...',
        'creators': 'Family name, First name: Affiliation (one author per line)',
        'thesis_supervisors': 'Family name, First name: Affiliation (one supervisor per line)',
        'keywords': 'One keyword per line...',
        'funding_source': 'Start typing a grant number, name or abbreviation...',
        'collections': 'Start typing a collection name...',
        'license': 'Start typing a license name or abbreviation...',
        'related_identifiers': 'e.g. 10.1234/foo.bar (one DOI per line)...',
        'conference_dates': 'e.g 21-22 November 2012...',
        'conference_place': 'e.g city, country...',
        'imprint_place': 'e.g city, country...',
        'imprint_isbn': 'e.g 0-06-251587-X',
    }

    field_state_mapping = {
        'access_right': {
            'open': (['license'], ['embargo_date']),
            'embargoed': (['embargo_date', 'license'], []),
            'restricted': ([], ['embargo_date', 'license']),
            'closed': ([], ['embargo_date', 'license']),
        },
        'upload_type': {
            'publication': (['publication_type', ], ['image_type']),
            'poster': ([], ['publication_type', 'image_type']),
            'presentation': ([], ['publication_type', 'image_type']),
            'dataset': ([], ['publication_type', 'image_type']),
            'image': (['image_type'], ['publication_type']),
            'video': ([], ['publication_type', 'image_type']),
            'audio': ([], ['publication_type', 'image_type']),
            '': ([], ['publication_type', 'image_type']),
        },
    }

    field_icons = {
        'thesis_university': 'building',
    }

    #
    # Methods
    #
    def get_field_icon(self, name):
        return self.field_icons.get(name, '')

    def get_field_by_name(self, name):
        try:
            return self._fields[name]
        except KeyError:
            return None

    def get_field_placeholder(self, name):
        return self.field_placeholders.get(name, "")

    def get_field_state_mapping(self, field):
        try:
            return self.field_state_mapping[field.short_name]
        except KeyError:
            return None

    def has_field_state_mapping(self, field):
        return field.short_name in self.field_state_mapping

    def has_autocomplete(self, field):
        return hasattr(field, 'autocomplete')

    #
    # Fields
    #
    upload_type = fields.UploadTypeField(validators=[validators.required()])
    publication_type = wtf.SelectField(
        label='Type of publication',
        choices=[
            ('book', 'Book'),
            ('section', 'Book section'),
            ('conferencepaper', 'Conference paper'),
            ('article', 'Journal article'),
            ('patent', 'Patent'),
            ('preprint', 'Preprint'),
            ('report', 'Report'),
            ('thesis', 'Thesis'),
            ('technicalnote', 'Technical note'),
            ('workingpaper', 'Working paper'),
            ('other', 'Other'),
        ],
        validators=[
            oa_validators.RequiredIf('upload_type', ['publication']),
            validators.optional()
        ],
    )
    image_type = wtf.SelectField(
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
        ]
    )

    #
    # Collection
    #
    collections = fields.CollectionsField(
        label="Collections",
        description="Attach your record to any number of collections.",
        filters=[
            splitchar_list(","),
        ]
    )

    #
    # Basic information
    #
    doi = fields.DOIField(
        label="Digital Object Identifier",
        description="Did your publisher already assign a DOI to your upload? If not, leave the field empty and we will register a new DOI for you. A DOI allow others to easily and unambiguously cite your upload.",
        filters=[
            strip_string,
            strip_doi,
        ]
    )
    publication_date = fields.Date(
        label=_('Publication date'),
        description='Format: YYYY-MM-DD. The date your upload was made available in case it was already published elsewhere.',
        default=date.today(),
        validators=[validators.required()]
    )
    title = fields.TitleField(
        validators=[validators.required()],
        filters=[
            strip_string,
        ],
    )
    creators = fields.AuthorField(
        label="Authors",
        validators=[validators.required()],
        description="Format: Family name, First name: Affiliation (one author per line)"
    )
    description = fields.AbstractField(
        label="Description",
        validators=[validators.required()],
        filters=[
            strip_string,
        ],
    )
    keywords = fields.KeywordsField(
        validators=[validators.optional()],
        filters=[
            splitlines_list
        ],
    )
    notes = wtf.TextAreaField(
        label="Additional notes",
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
        description="Open access uploads have considerably higher visibility on %s. Additionally, we only register DOIs for Open Access and Embargoed Access uploads." % CFG_SITE_NAME,
        default="open",
        validators=[validators.required()]
    )
    embargo_date = fields.Date(
        label=_('Embargo date'),
        description='Format: YYYY-MM-DD. The date your upload will be made publicly available in case it is under an embargo period from your publisher.',
        default=date.today(),
        validators=[
            oa_validators.RequiredIf('access_right', ['embargoed']),
            validators.optional()
        ]
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
        description='The selected license applies to all of your files displayed in the bottom of the form. If you want to upload some files under a different license, please do so in two separate uploads. If you think a license missing in the list, please inform us at %s.' % CFG_SITE_SUPPORT_EMAIL,
        filters=[
            strip_string,
        ],
    )

    #
    # Funding
    #
    funding_source = fields.FundingField(
        label="Grants",
        description="Note, a human %s curator will validate your upload before reporting it to OpenAIRE, and you may thus experience a delay up to 1 working day before your upload is available in OpenAIRE." % CFG_SITE_NAME,
        filters=[
            splitchar_list(","),
        ]
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
        description="Format: e.g. 10.1234/foo.bar (one DOI per line)."
    )  # List identifier, rel type

    #
    # Journal
    #
    journal_title = fields.JournalField()
    journal_volume = wtf.TextField(label="Volume")
    journal_issue = wtf.TextField(label="Issue")
    journal_pages = wtf.TextField(label="Pages")

    #
    # Book/report/chapter
    #
    partof_title = wtf.TextField(label="Book title", description="Title of the book or report which this upload is part of.")
    partof_pages = wtf.TextField(label="Pages")

    imprint_isbn = wtf.TextField(label="ISBN")
    imprint_publisher = wtf.TextField(label="Publisher")
    imprint_place = wtf.TextField(label="Place")

    #
    # Thesis
    #
    thesis_supervisors = fields.AuthorField(
        label="Supervisors",
        validators=[validators.optional()],
        description="Format: Family name, First name: Affiliation (one supervisor per line)"
    )
    thesis_university = wtf.TextField(
        label='Awarding University',
        validators=[validators.optional()],
    )
    thesis_university._icon_html = '<i class="icon-building"></i>',

    #
    # Conference
    #
    conference_title = wtf.TextField()
    conference_acronym = wtf.TextField(label="Acronym")
    conference_dates = wtf.TextField(label="Dates")
    conference_place = wtf.TextField(label="Place")
    conference_url = wtf.TextField(label="Website")


#DepostionForm.thesis_university._icon_html = '<i class="icon-building"></i>'
#DepostionForm._fields['thesis_university']._icon_html = '<i class="icon-building"></i>'
