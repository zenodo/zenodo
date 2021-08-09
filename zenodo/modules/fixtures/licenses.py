# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
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

"""Zenodo license fixture loading."""

from __future__ import absolute_import, print_function, unicode_literals

import json
from collections import OrderedDict

from flask import current_app
from invenio_db import db
from invenio_opendefinition.minters import license_minter
from invenio_opendefinition.resolvers import license_resolver
from invenio_opendefinition.validators import license_validator
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records.api import Record
from invenio_pidstore.errors import PIDAlreadyExists

from .utils import read_json


def find_matching_licenses(legacy_licenses, od_licenses):
    """Match the licenses from the legacy set with open definition licenses.

    :param legacy_licenses: Zenodo legacy licenses.
    :type legacy_licenses: list of dict
    :param od_licenses: OpenDefinition.org licenses.
    :type od_licenses: list of dict
    """
    fixed = {
      "cc-zero": "CC0-1.0",
      "cc-by-sa": "CC-BY-SA-4.0",
      "cc-by-nc-4.0": "CC-BY-NC-4.0",
      "cc-by-nd-4.0": "CC-BY-ND-4.0",
      "cc-by": "CC-BY-4.0",
      "agpl-v3": "AGPL-3.0",
      "apache2.0": "Apache-2.0",
      "apache": "Apache-2.0",
      "bsl1.0": "BSL-1.0",
      "cuaoffice": "CUA-OPL-1.0",
      "ecl2": "ECL-2.0",
      "ver2_eiffel": "EFL-2.0",
      "lucent1.02": "LPL-1.02",
      "pythonsoftfoundation": "Python-2.0",
      "qtpl": "QPL-1.0",
      "real": "RPSL-1.0",
      "vovidapl": "VSL-1.0",
      "ukcrown-withrights": "ukcrown-withrights",
      "sun-issl": "SISSL",
      "pythonpl": "CNRI-Python",
    }

    matchers = (
        ("Fixed", lambda z, o: z['id'] in fixed and fixed[z['id']] == o['id']),
        ("ID", lambda z, o: z['id'] == o['id']),
        ("ID_Upper", lambda z, o: z['id'].upper() == o['id'].upper()),
        ("URL", lambda z, o: z['url'] and z['url'] == o['url']),
        ("URL_Upper", lambda z, o: z['url'] and
            z['url'].upper() == o['url'].upper()),
        ("Z title in O", lambda z, o: z['title'] and
            o['title'].upper().startswith(z['title'].upper())),
        ("O title in Z", lambda z, o: z['title'] and
            z['title'].upper().startswith(o['title'].upper())),
    )

    missing = []
    matched = []
    for zl in legacy_licenses:
        found = False
        for m_name, m_fun in matchers:
            for ol in od_licenses:
                if m_fun(zl, ol):
                    matched.append((zl, ol, m_name))
                    found = True
                    break
            if found:
                break
        if not found:
            missing.append(zl)
    return matched, missing


def matchlicenses(legacy_lic_filename, od_filename, destination):
    """Generate the JSON with the licenses mapping."""
    with open(legacy_lic_filename, "r") as fp:
        legacy_licenses = json.load(fp)
    with open(od_filename, "r") as fp:
        od_licenses = json.load(fp)
    if isinstance(od_licenses, dict):
        od_licenses = [v for k, v in od_licenses.items()]
    matched, missing = find_matching_licenses(legacy_licenses, od_licenses)

    mapping = OrderedDict((l1['id'], l2['id']) for l1, l2, _ in matched)
    with open(destination, 'w') as fp:
        json.dump(mapping, fp, indent=2)


def update_legacy_meta(license):
    """Update the Zenodo legacy terms for license metadata.

    Updates the metadata in order to conform with opendefinition schema.
    """
    l = dict(license)
    if 'od_conformance' not in l:
        l['od_conformance'] = 'approved' if l['is_okd_compliant'] \
            else 'rejected'
    if 'osd_conformance' not in l:
        l['osd_conformance'] = 'approved' if l['is_osi_compliant'] \
            else 'rejected'
    l.pop('is_okd_compliant', None)
    l.pop('is_osi_compliant', None)
    l['$schema'] = 'http://{0}{1}/{2}'.format(
        current_app.config['JSONSCHEMAS_HOST'],
        current_app.config['JSONSCHEMAS_ENDPOINT'],
        current_app.config['OPENDEFINITION_SCHEMAS_DEFAULT_LICENSE']
    )
    return l


def create_new_license(license):
    """Create a new license record.

    :param license: License dictionary to be loaded.
    :type license: dict
    """
    license = update_legacy_meta(license)
    license_validator.validate(license)
    record = Record.create(license)
    license_minter(record.id, license)


def loadlicenses():
    """Load Zenodo licenses.

    Create extra PID if license is to be mapped and already exists, otherwise
    create a new license record and a PID.
    """
    data = read_json('data/licenses.json')
    map_ = read_json('data/licenses_map.json')
    mapped = [(d, map_[d['id']] if d['id'] in map_ else None) for d in data]
    try:
        for lic, alt_pid in mapped:
            if lic['id'] == alt_pid:  # Skip the already-existing licenses
                continue
            if alt_pid:
                try:
                    pid, record = license_resolver.resolve(alt_pid)
                    license_minter(record.id, lic)
                except PIDDoesNotExistError:
                    try:
                        create_new_license(lic)
                    except PIDAlreadyExists:
                        db.session.rollback()
            else:
                try:
                    create_new_license(lic)
                except PIDAlreadyExists:
                    db.session.rollback()
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
