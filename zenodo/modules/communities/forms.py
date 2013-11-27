"""WebAccount Forms"""

from invenio.webinterface_handler_flask_utils import _
from invenio.wtforms_utils import InvenioForm as Form
from flask.ext import wtf
from sqlalchemy.exc import SQLAlchemyError

from wtforms import SubmitField, Field, validators
from invenio.wtforms_utils import InvenioForm as Form, InvenioBaseForm
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
    }

    field_state_mapping = {
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
        description='Required. Only letters, numbers and dash are allowed. The identifier is used in the URL for the community collection, and cannot be modified later.',
        validators=[validators.required(), validators.length(max=100, message="The identifier must be less than 100 characters long."), validators.regexp(u'^[-\w]+$', message='Only letters, numbers and dash are allowed')]
    )

    title = wtf.TextField(
        description='Required.',
        validators=[validators.required()]
    )

    description = wtf.TextAreaField(
        description='Optional. A short description of the community collection, which will be displayed on the index page of the community.',
    )

    curation_policy = wtf.TextAreaField(
        description='Optional. Please describe short and precise the policy by which you accepted/reject new uploads in this community.',
    )

    page = wtf.TextAreaField(
        description='Optional. A long description of the community collection, which will be displayed on a separate page linked from the index page.',
    )

    field_icons = {
        'identifier': 'barcode',
        'title': 'file-alt',
        'description': 'pencil',
        'curation_policy': 'check',
    }

    #
    # Validation
    #
    def validate_identifier(self, field):
        if field.data:
            field.data = field.data.lower()
            if UserCollection.query.filter_by(id=field.data).first():
                raise wtf.ValidationError("The identifier already exists. Please choose a different one.")


class EditCollectionForm(CollectionForm):
    """
    Same as collection form, except identifier is removed.
    """
    identifier = None


class DeleteCollectionForm(InvenioBaseForm):
    """
    Form to confirm deletion of a collection:
    """
    delete = wtf.HiddenField(default='yes', validators=[validators.required()])
