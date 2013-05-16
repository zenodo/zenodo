# -*- coding: utf-8 -*-
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
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from flask import current_app
from flask.ext.admin import Admin, BaseView, AdminIndexView
from flask.ext.admin.contrib.sqlamodel import ModelView
from invenio.webinterface_handler_flask_utils import InvenioBlueprint
from invenio.webuser_flask import current_user


def can_acc_action(action):
    """
    Return getter/setter for can_<action> properties
    """
    def fget(self):
        return self.acc_authorize(action)

    def fset(self, value):
        setattr(self, '_can_%s' % action, value)

    def fdel(self):
        delattr(self, '_can_%s' % action)

    return (fget, fset, fdel)


#
# Base classes
#
class InvenioBaseView(BaseView):
    """
    BaseView for administration interfaces
    """
    acc_view_action = None

    can_view = property(*can_acc_action('view'))

    def acc_authorize(self, action):
        """ Check authorization for a given action """
        # First check if _can_<action> is set.
        if not getattr(self, '_can_%s' % action, True):
            return False

        # Next check if user is authorized to edit
        action = getattr(self, 'acc_%s_action' % action, None)
        if action:
            return self.blueprint.invenio_authorized(action)
        else:
            return current_user.is_super_admin

    def is_accessible(self):
        """
        Check if admin interface is accessible by the current user
        """
        if not current_user.is_authenticated():
            return False
        return self.can_view

    def create_blueprint(self, admin):
        """
        Create Flask blueprint.

        Copy/pasted from  from flask.ext.admin.BaseView, with minor edits.
        """
        # Store admin instance
        self.admin = admin

        # If endpoint name is not provided, get it from the class name
        if self.endpoint is None:
            self.endpoint = self.__class__.__name__.lower()

        # If the static_url_path is not provided, use the admin's
        if not self.static_url_path:
            self.static_url_path = admin.static_url_path

        # If url is not provided, generate it from endpoint name
        if self.url is None:
            if self.admin.url != '/':
                self.url = '%s/%s' % (self.admin.url, self.endpoint)
            else:
                if self == admin.index_view:
                    self.url = '/'
                else:
                    self.url = '/%s' % self.endpoint
        else:
            if not self.url.startswith('/'):
                self.url = '%s/%s' % (self.admin.url, self.url)

        # If we're working from the root of the site, set prefix to None
        if self.url == '/':
            self.url = None

        # If name is not povided, use capitalized endpoint name
        if self.name is None:
            self.name = self._prettify_name(self.__class__.__name__)

        import_name = getattr(self, 'import_name', __name__)

        # Create blueprint and register rules
        self.blueprint = InvenioBlueprint(
            self.endpoint, import_name,
            url_prefix=self.url,
            subdomain=self.admin.subdomain,
            template_folder='templates',
            static_folder=self.static_folder,
            static_url_path=self.static_url_path,
            force_https=True,
        )

        for url, name, methods in self._urls:
            self.blueprint.add_url_rule(url,
                                        name,
                                        getattr(self, name),
                                        methods=methods)

        return self.blueprint


class InvenioModelView(ModelView, InvenioBaseView):
    """
    Invenio Admin base view for SQL alchemy models
    """
    acc_edit_action = None
    acc_delete_action = None
    acc_create_action = None

    can_delete = property(*can_acc_action('delete'))
    can_edit = property(*can_acc_action('edit'))
    can_create = property(*can_acc_action('create'))


class InvenioAdminIndexView(AdminIndexView, InvenioBaseView):
    """
    Invenio admin index view that ensures InvenioBlueprint is being used.
    """

    import_name = 'flask_admin'
    """ Ensures that templates and static files can be found """


#
# Utility method
#
def register_admin(app):
    """
    Register all administration views with the Flask application
    """
    from invenio.errorlib import register_exception
    from invenio.importutils import autodiscover_modules

    # Initialize app
    admin.init_app(app)

    # Call register() in admin module to register views.
    modules = autodiscover_modules(['invenio'], '.+_admin\.py')
    for m in modules:
        register_func = getattr(m, 'register_admin', None)
        if register_func and callable(register_func):
            try:
                register_func(app, admin)
            except Exception:
                register_exception()


#
# Flask-Admin instance
#
admin = Admin(name="Invenio", index_view=InvenioAdminIndexView(), base_template="admin_base.html")
