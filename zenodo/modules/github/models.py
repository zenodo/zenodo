
from invenio.modules.accounts.models import User
from invenio.ext.sqlalchemy import db

#
# Configuration variables
#
class OAuthTokens(db.Model):
    """ Represents an OAuth token
    """
    
    __tablename__ = 'oauth_tokens'
    
    #
    # Fields
    #
    id = db.Column(
        db.Integer(100, unsigned=True),
        primary_key=True,
        autoincrement=True
    )
    
    client_id = db.Column(
        db.String(255),
        nullable=False
    )
    
    user_id = db.Column(
        db.Integer(15, unsigned=True), db.ForeignKey(User.id),
        nullable=False
    )
    
    access_token = db.Column(
        db.Text(),
        nullable=False
    )
    
    extra_data = db.Column(
        db.JSON,
        nullable=True
    )