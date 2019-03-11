# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016, 2017 CERN.
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

"""Blueprint for Zenodo-Records."""

from __future__ import absolute_import, print_function, unicode_literals

import copy
from operator import itemgetter

import idutils
import six
from flask import Blueprint, current_app, render_template, request
from flask_principal import ActionNeed
from invenio_access.permissions import Permission
from invenio_communities.models import Community
from invenio_formatter.filters.datetime import from_isodate
from invenio_i18n.ext import current_i18n
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_previewer.proxies import current_previewer
from invenio_records_ui.signals import record_viewed
from werkzeug.utils import import_string

from zenodo.modules.communities.api import ZenodoCommunity
from zenodo.modules.records.utils import is_doi_locally_managed
from zenodo.modules.stats.utils import get_record_stats

from .api import ZenodoRecord
from .models import AccessRight, ObjectType
from .permissions import RecordPermission
from .serializers import citeproc_v1

blueprint = Blueprint(
    'zenodo_records',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/search'
)


#
# Access right template filters and tests.
#
@blueprint.app_template_test('accessright')
def is_valid_accessright(value):
    """Test if access right is valid."""
    return AccessRight.is_valid(value)


@blueprint.app_template_test('embargoed')
def is_embargoed(embargo_date, accessright=None):
    """Test if date is still embargoed (according to UTC date."""
    if accessright is not None and accessright != AccessRight.EMBARGOED:
        return False
    if embargo_date is not None:
        return AccessRight.is_embargoed(embargo_date)
    return False


@blueprint.app_template_filter('pidstatus')
def pidstatus_title(pid):
    """Get access right.

    Better than comparing record.access_right directly as access_right
    may have not yet been updated after the embargo_date has passed.
    """
    return PIDStatus(pid.status).title


@blueprint.app_template_filter()
def accessright_get(value, embargo_date=None):
    """Get access right.

    Better than comparing record.access_right directly as access_right
    may have not yet been updated after the embargo_date has passed.
    """
    return AccessRight.get(value, embargo_date)


@blueprint.app_template_filter()
def accessright_category(value, embargo_date=None, **kwargs):
    """Get category for access right."""
    return AccessRight.as_category(
        AccessRight.get(value, embargo_date=embargo_date), **kwargs)


@blueprint.app_template_filter()
def make_query(values):
    """Get category for access right."""
    parts = []
    for k, v in values.items():
        parts.append(u'{0}:"{1}"'.format(k, v))
    return u' '.join(parts)


@blueprint.app_template_filter()
def accessright_title(value, embargo_date=None):
    """Get category for access right."""
    return AccessRight.as_title(
        AccessRight.get(value, embargo_date=embargo_date))


@blueprint.app_template_filter()
def accessright_icon(value, embargo_date=None):
    """Get icon for access right."""
    return AccessRight.as_icon(AccessRight.get(value, embargo_date))


@blueprint.app_template_filter()
def accessright_description(value, embargo_date=None):
    """Get a description for access right."""
    return AccessRight.as_description(
        AccessRight.get(value, embargo_date),
        from_isodate(embargo_date)
    )


@blueprint.app_template_filter()
def has_record_perm(user, record, action):
    """Check if user has a given record permission."""
    return RecordPermission.create(record, action, user=user).can()


#
# Related identifiers filters.
#
@blueprint.app_template_filter('zenodo_related_links')
def zenodo_related_links(record, communities):
    """Get logos for related links."""
    def apply_rule(item, rule):
        r = copy.deepcopy(rule)
        r['link'] = idutils.to_url(item['identifier'], item['scheme'], 'https')
        return r

    def match_rules(item):
        rs = []
        for c in set(communities):
            if c.id in current_app.config['ZENODO_RELATION_RULES']:
                rules = current_app.config['ZENODO_RELATION_RULES'][c.id]
                for r in rules:
                    if item['relation'] == r['relation'] and \
                       item['scheme'] == r['scheme'] and \
                       item['identifier'].startswith(r['prefix']):
                        rs.append(r)
        return rs

    ret = []
    for item in record.get('related_identifiers', []):
        for r in match_rules(item):
            ret.append(apply_rule(item, r))

    return ret


#
# Community branding filters
#
@blueprint.app_template_filter('zenodo_community_branding_links')
def zenodo_community_branding_links(record):
    """Get logos for branded communities."""
    comms = record.get('communities', [])
    branded = current_app.config['ZENODO_COMMUNITY_BRANDING']
    ret = []
    for comm in comms:
        if comm in branded:
            comm_model = Community.query.get(comm)
            ret.append((comm, comm_model.logo_url))
    return ret


#
# Object type template filters and tests.
#
@blueprint.app_template_filter()
def objecttype(value):
    """Get object type."""
    return ObjectType.get_by_dict(value)


@blueprint.app_template_filter()
def contributortype_title(value):
    """Get object type."""
    return current_app.config.get('DEPOSIT_CONTRIBUTOR_TYPES_LABELS', {}).get(
        value, value)


@blueprint.app_template_filter()
def meeting_title(m):
    """Get meeting title."""
    acronym = m.get('acronym')
    title = m.get('title')
    if acronym and title:
        return u'{0} ({1})'.format(title, acronym)
    else:
        return title or acronym


#
# Files related template filters.
#
@blueprint.app_template_filter()
def select_preview_file(files):
    """Get list of files and select one for preview."""
    selected = None
    try:
        for f in sorted(files or [], key=itemgetter('key')):
            if f['type'] in current_previewer.previewable_extensions:
                if selected is None:
                    selected = f
                elif f['default']:
                    selected = f
    except KeyError:
        pass
    return selected


#
# Stats filters
#

@blueprint.app_template_filter()
def record_stats(record):
    """Fetch record statistics from Elasticsearch."""
    return get_record_stats(record.id, False)


@blueprint.app_template_filter()
def stats_num_format(num):
    """Format a statistics value."""
    return '{:,.0f}'.format(num or 0)


#
# Persistent identifiers template filters
#
@blueprint.app_template_test()
def local_doi(value):
    """Test if a DOI is a local DOI."""
    prefixes = current_app.config.get('ZENODO_LOCAL_DOI_PREFIXES', [])
    return prefixes and any((value.startswith(p + "/") for p in prefixes))


@blueprint.app_template_filter('relation_title')
def relation_title(relation):
    """Map relation type to title."""
    return dict(current_app.config['ZENODO_RELATION_TYPES']).get(relation) or \
        relation


@blueprint.app_template_filter('citation')
def citation(record, pid, style=None, ln=None):
    """Render citation for record according to style and language."""
    locale = ln or current_i18n.language
    style = style or 'science'
    try:
        return citeproc_v1.serialize(pid, record, style=style, locale=locale)
    except Exception:
        current_app.logger.exception(
            'Citation formatting for record {0} failed.'
            .format(str(record.id)))
        return None


@blueprint.app_template_filter('pid_url')
def pid_url(identifier, scheme=None, url_scheme='https'):
    """Convert persistent identifier into a link."""
    if scheme is None:
        try:
            scheme = idutils.detect_identifier_schemes(identifier)[0]
        except IndexError:
            scheme = None
    try:
        if scheme and identifier:
            return idutils.to_url(identifier, scheme, url_scheme=url_scheme)
    except Exception:
        current_app.logger.warning('URL generation for identifier {0} failed.'
                                   .format(identifier), exc_info=True)
    return ''


@blueprint.app_template_filter('doi_locally_managed')
def doi_locally_managed(pid):
    """Determine if DOI is managed locally."""
    return is_doi_locally_managed(pid)


@blueprint.app_template_filter()
def pid_from_value(pid_value, pid_type='recid'):
    """Determine if DOI is managed locally."""
    try:
        return PersistentIdentifier.get(pid_type=pid_type, pid_value=pid_value)
    except Exception:
        pass


@blueprint.app_template_filter()
def record_from_pid(recid):
    """Get record from PID."""
    try:
        return ZenodoRecord.get_record(recid.object_uuid)
    except Exception:
        return {}


def records_ui_export(pid, record, template=None, **kwargs):
    """Record serialization view.

    Plug this method into your ``RECORDS_UI_ENDPOINTS`` configuration:

    .. code-block:: python

        RECORDS_UI_ENDPOINTS = dict(
            recid=dict(
                # ...
                route='/records/<pid_value/files/<filename>',
                view_imp='zenodo.modules.records.views.records_ui_export',
            )
        )
    """
    formats = current_app.config.get('ZENODO_RECORDS_EXPORTFORMATS')
    fmt = request.view_args.get('format')

    if formats.get(fmt) is None:
        return render_template(
            'zenodo_records/records_export_unsupported.html'), 410
    else:
        serializer = import_string(formats[fmt]['serializer'])
        data = serializer.serialize(pid, record)
        if isinstance(data, six.binary_type):
            data = data.decode('utf8')

        # emit record_viewed event
        record_viewed.send(
            current_app._get_current_object(),
            pid=pid,
            record=record,
        )
        return render_template(
            template, pid=pid, record=record,
            data=data, format_title=formats[fmt]['title'])


def _can_curate(community, user, record, accepted=False):
    """Determine whether user can curate given community."""
    if (community.id_user == user.get_id()) or \
            (accepted and (user.get_id() in record.get('owners', []))):
        return True
    return False


def community_curation(record, user):
    """Generate a list of pending and accepted communities with permissions.

    Return a 4-tuple of lists (in order):
     * 'pending' communities, which can be curated by given user
     * 'accepted' communities, which can be curated by given user
     * All 'pending' communities
     * All 'accepted' communities
    """
    irs = ZenodoCommunity.get_irs(record).all()
    pending = list(set(ir.community for ir in irs))
    accepted = [Community.get(c) for c in record.get('communities', [])]
    # Additionally filter out community IDs that did not resolve (None)
    accepted = [c for c in accepted if c]

    # Check for global curation permission (all communities on this record).
    global_perm = None
    if user.is_anonymous:
        global_perm = False
    elif Permission(ActionNeed('admin-access')).can():
        global_perm = True

    if global_perm:
        return (pending, accepted, pending, accepted)
    else:
        return (
            [c for c in pending if _can_curate(c, user, record)],
            [c for c in accepted
             if _can_curate(c, user, record, accepted=True)],
            pending,
            accepted,
        )


def record_communities():
    """Context processor for community curation for given record."""
    return dict(community_curation=community_curation)
