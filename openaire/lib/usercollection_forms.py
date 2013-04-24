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
from invenio.usercollection_model import UserCollection


#
# Form
#
class CollectionForm(Form):
    """
    ZENODO collection form
    """
    field_sets = [
        ('Information', [
            'identifier', 'title', 'description', 'curation_policy',
            'page'
        ], {'classes': 'in'}),
    ]

    field_placeholders = {
        'doi': 'e.g. 10.1234/foo.bar...',
        'creators': 'Family name, First name: Affiliation (one author per line)',
        'thesis_supervisors': 'Family name, First name: Affiliation (one supervisor per line)',
        'keywords': 'One keyword per line...',
        'funding_source': 'Start typing a grant number, name or abbreviation...',
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
    identifier = wtf.TextField(
        label=_('Identifier'),
        description='Required. Only letters, numbers and dash are allowed. The identifier is used in the URL for the collection, and cannot be modified later.',
        validators=[validators.required(), validators.regexp(u'^[-\w]+$', message='Only letters, numbers and dash are allowed')]
    )

    title = wtf.TextField(
        description='Required.',
        validators=[validators.required()]
    )

    description = wtf.TextAreaField(
        description='Optional. A short description of the collection, which will be displayed on the index page of the collection.',
    )

    curation_policy = wtf.TextAreaField(
        description='Optional. Please describe short and precise the policy by which you accepted/reject new uploads in this collection.',
    )

    page = wtf.TextAreaField(
        description='Optional. A long description of the collection, which will be displayed on a separate page linked from the index page of the collection.',
    )

    field_icons = {
        'identifier': 'barcode',
        'title': 'book',
        'description': 'pencil',
    }

    #
    # Validation
    #
    def validate_identifier(self, field):
        if field.data:
            if UserCollection.query.filter_by(id=field.data).first():
                raise wtf.ValidationError("The identifier already exists. Please choose a different one.")


class EditCollectionForm(CollectionForm):
    identifier = None
