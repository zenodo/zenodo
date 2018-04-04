# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2018 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Admin view for updating datacite metadata."""

import uuid
from datetime import datetime

from flask import current_app, flash, redirect, request, url_for
from flask_admin import BaseView, expose
from flask_babelex import lazy_gettext as _
from flask_wtf import FlaskForm
from invenio_cache import current_cache
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired

from zenodo.modules.records.utils import find_registered_doi_pids


class UpdateDataciteForm(FlaskForm):
    """Form for updating datacite metadata."""

    from_date = DateField(
        _('From'),
        description=_('Required.'),
        validators=[DataRequired()],
    )

    until_date = DateField(
        _('Until'),
        description=_('Required.'),
        validators=[DataRequired()],
    )


class UpdateDataciteView(BaseView):
    """View for updating datacite metadata."""

    @expose('/', methods=('GET', 'POST'))
    def update_datacite(self):
        """."""
        form = UpdateDataciteForm()
        cancel_or_new_task_form = FlaskForm()

        is_task_running = False
        time = 0
        task_details = current_cache.get('update_datacite:task_details')

        if task_details:
            is_task_running = True
            if cancel_or_new_task_form.validate_on_submit():
                current_cache.set('update_datacite:task_details', None)
                return redirect(url_for('updatedataciteview.update_datacite'))
        else:
            if form.validate_on_submit():
                from_date = request.form['from_date']
                until_date = request.form['until_date']

                action = request.form['action']
                if action == 'SubmitDates':
                    if from_date > until_date:
                        flash("Error: the 'From' date should precede the 'Until' date.")
                    else:
                        pids_count = find_registered_doi_pids(from_date,
                                                                until_date,
                                                                current_app.config['ZENODO_LOCAL_DOI_PREFIXES']).count()
                        task_details = dict(
                            total_pids=pids_count
                        )
                        time = pids_count/current_app.config['DATACITE_UPDATING_RATE_PER_HOUR']

                elif action == 'Confirm':
                    pids_count = find_registered_doi_pids(from_date,
                                                          until_date,
                                                          current_app.config['ZENODO_LOCAL_DOI_PREFIXES']).count()
                    task_details = dict(
                        start_date=datetime.utcnow(),
                        job_id=str(uuid.uuid4()),
                        from_date=from_date,
                        until_date=until_date,
                        total_pids=pids_count,
                        left_pids=pids_count,
                        last_update=datetime.utcnow()
                    )
                    current_cache.set('update_datacite:task_details',
                                      task_details, timeout=-1)
                    return redirect(url_for('updatedataciteview.update_datacite'))

                elif action == 'Cancel':
                    return redirect(url_for('updatedataciteview.update_datacite'))

        return self.render('zenodo_records/update_datacite.html',
                           form=form,
                           cancel_or_new_task_form=cancel_or_new_task_form,
                           details=task_details,
                           is_task_running=is_task_running, time=time)


updatedatacite_adminview = {
    'view_class': UpdateDataciteView,
    'kwargs': {'name': 'Update Datacite', 'category': 'Records'},

}
