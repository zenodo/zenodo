# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2012, 2013 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import json

from flask import render_template, url_for, request
from flask.ext.restful import fields, marshal

from invenio.restapi import UTCISODateTimeString
from invenio.config import CFG_DATACITE_DOI_PREFIX
from invenio.bibformat import format_record
from invenio.bibknowledge import get_kb_mapping
from invenio.webuser_flask import current_user
from invenio.webdeposit_load_forms import forms
from invenio.webdeposit_models import DepositionType, Deposition, \
    InvalidApiAction
from invenio.webdeposit_workflow_tasks import render_form, \
    create_recid, \
    prepare_sip, \
    finalize_record_sip, \
    upload_record_sip, \
    mint_pid, \
    prefill_draft
from invenio.zenodoutils import create_doi, filter_empty_helper
from invenio.bibtask import task_low_level_submission
from invenio.restapi import error_codes


__all__ = ['upload']

CFG_LICENSE_KB = "licenses"
CFG_LICENSE_SOURCE = "opendefinition.org"
CFG_ZENODO_USER_COLLECTION_ID = "zenodo"
CFG_ECFUNDED_USER_COLLECTION_ID = "ecfunded"


def process_sip():
    def _process_sip(obj, dummy_eng):
        d = Deposition(obj)
        recjson = d.get_latest_sip(include_sealed=False).metadata

        # Owner of record (can edit/view the record)
        email = current_user.info.get('email', '')
        recjson['owner'] = dict(
            email=email,
            username=current_user.info.get('nickname', ''),
            id=current_user.get_id(),
        )

        # ===========
        # Communities
        # ===========
        try:
            # Extract identifier (i.e. elements are mapped from dict ->
            # string)
            recjson['provisional_communities'] = map(
                lambda x: x['identifier'],
                recjson.get('provisional_communities', [])
            )

            # Specific ZENODO user collection, used to curate content for
            # ZENODO
            recjson['provisional_communities'].append(
                CFG_ZENODO_USER_COLLECTION_ID
            )

            # Specific ZENODO user collection for OpenAIRE (used to curate
            # FP7 funded research)
            if recjson.get('grants', []):
                recjson['provisional_communities'].append(
                    CFG_ECFUNDED_USER_COLLECTION_ID
                )

            recjson['provisional_communities'] = list(set(
                recjson['provisional_communities']
            ))
        except TypeError:
            # Happens on re-run
            pass

        # =================
        # Files
        # =================
        # Generate firerole
        fft_status = []
        if recjson['access_right'] == 'open':
            # Access to everyone
            fft_status = [
                'allow any',
            ]
        elif recjson['access_right'] == 'embargoed':
            # Access to submitted, Deny everyone else until embargo date,
            # then allow all
            fft_status = [
                'allow email "%s"' % email,
                'deny until "%s"' % recjson['embargo_date'].isoformat(),
                'allow any',
            ]
        elif recjson['access_right'] in ('closed', 'restricted',):
            # Access to submitter, deny everyone else
            fft_status = [
                'allow email "%s"' % email,
                'deny all',
            ]

        fft_status = "firerole: %s" % "\n".join(fft_status)
        # Calculate number of leading zeros needed in the comment.
        file_commment_fmt = "%%0%dd" % len(str(len(recjson['fft'])))

        for idx, f in enumerate(recjson['fft']):
            f['restriction'] = fft_status
            # Bibdocfile does not have any concept of ordering, nor will
            # bibupload keep the order of FFT tags for the MARC field 8564.
            # Hence, this trick stores the ordering of files for a record in
            # the files comment, so files can be alphabetically sorted (i.e. we
            # we add leading zeores) by their comment.
            f['comment'] = file_commment_fmt % idx

        # =================
        # License
        # =================
        if recjson['access_right'] in ["open", "embargoed"]:
            info = get_kb_mapping(CFG_LICENSE_KB, str(recjson['license']))
            if info:
                info = json.loads(info['value'])
                recjson['license'] = dict(
                    identifier=recjson['license'],
                    source=CFG_LICENSE_SOURCE,
                    license=info['title'],
                    url=info['url'],
                )
        elif 'license' in recjson:
            del recjson['license']

        # =================
        # Grants
        # =================
        # Remap incoming dictionary
        recjson['grants'] = map(
            lambda x: dict(
                title="%s - %s (%s)" % (x['acronym'], x['title'], x['id']),
                identifier=x['id']
            ),
            recjson.get('grants', [])
        )

        # =======================
        # Journal
        # =======================
        # Set year or delete fields if no title is provided
        if recjson.get('journal.title', None):
            recjson['journal.year'] = recjson['publication_date'].year

        # =======================
        # Book/chaper/report
        # =======================
        if 'imprint.publisher' in recjson and 'imprint.place' in recjson:
            recjson['imprint.year'] = recjson['publication_date'].year

        if 'part_of.title' in recjson:
            mapping = [
                ('part_of.publisher', 'imprint.publisher'),
                ('part_of.place', 'imprint.place'),
                ('part_of.year', 'imprint.year'),
                ('part_of.isbn', 'isbn'),
            ]
            for new, old in mapping:
                if old in recjson:
                    try:
                        recjson[new] = recjson[old]
                        del recjson[old]
                    except KeyError:
                        pass

        # =================
        # Conference
        # =================
        if 'conference_url' in recjson:
            recjson['url'] = dict(
                url=recjson['conference_url'],
                description='Conference website',
                format=None,  # Needed because of str.format
            )
            del recjson['conference_url']

        # =======================
        # Filter out empty fields
        # =======================
        list_fields = [
            'authors', 'keywords', 'thesis_supervisors'
        ]
        for key in list_fields:
            recjson[key] = filter(
                filter_empty_helper(), recjson.get(key, [])
            )

        recjson['related_identifiers'] = filter(
            filter_empty_helper(keys=['identifier']),
            recjson['related_identifiers']
        )

        d.update()
    return _process_sip


def check_existing_pid(pid, recjson):
    """
    In Zenodo an existing pid is either 1) pre-reserved and should be minted or
    2) external and should not be minted. A user cannot enter a Zenodo pid by
    themselves.
    """
    reserved_doi = recjson.get('prereserve_doi', None)
    if reserved_doi and reserved_doi['doi'] == pid:
        return True
    return False


def run_tasks():
    """
    Run bibtasklet and webcoll after upload.
    """
    def _run_tasks(obj, dummy_eng):
        d = Deposition(obj)
        sip = d.get_latest_sip(include_sealed=True)

        recid = sip.metadata['recid']
        communities = sip.metadata['provisional_communities']

        common_args = ['-P5', ]
        sequenceid = getattr(d.workflow_object, 'task_sequence_id', None)
        if sequenceid:
            common_args += ['-I', str(sequenceid)]

        task_low_level_submission(
            'bibtasklet', 'webdeposit', '-T', 'bst_openaire_new_upload',
            '--argument', 'recid=%s' % recid, *common_args
        )

        for c in communities:
            task_low_level_submission(
                'webcoll', 'webdeposit', '-c', 'provisional-user-%s' % c,
                *common_args
            )
    return _run_tasks


def reserved_recid():
    """
    Check for existence of a reserved recid and put in metadata so
    other tasks are not going to reserve yet another recid.
    """
    def _reserved_recid(obj, dummy_eng):
        d = Deposition(obj)
        sip = d.get_latest_sip(include_sealed=False)
        reserved_doi = sip.metadata.get('prereserve_doi', None)

        if reserved_doi and reserved_doi['recid']:
            sip.metadata['recid'] = reserved_doi['recid']

        d.update()
    return _reserved_recid


def api_validate_files():
    """
    Check for existence of a reserved recid and put in metadata so
    other tasks are not going to reserve yet another recid.
    """
    def _api_validate_files(obj, eng):
        if getattr(request, 'is_api_request', False):
            d = Deposition(obj)
            if len(d.files) < 1:
                d.set_render_context(dict(
                    message="Bad request",
                    status=400,
                    errors=[dict(
                        message="Minimum one file must be provided.",
                        code=error_codes['validation_error']
                    )],
                ))
                d.update()
                eng.halt("API: No files provided")
            else:
                # Mark all drafts as completed
                for draft in d.drafts.values():
                    draft.complete()
                d.update()
    return _api_validate_files


class upload(DepositionType):
    """
    ZENODO deposition workflow
    """
    workflow = [
        # Load pre-filled data from cache
        prefill_draft(draft_id='_default'),
        # Render the form and wait until it is completed
        render_form(draft_id='_default'),
        # Test if all files are available for API
        api_validate_files(),
        # Create the submission information package by merging data from
        # all drafts - i.e. generate the recjson.
        prepare_sip(),
        # Check for reserved recids.
        reserved_recid(),
        # Reserve a new record id
        create_recid(),
        # Register DOI in internal pid store.
        mint_pid(
            pid_field='doi',
            pid_store_type='doi',
            pid_creator=lambda recjson: create_doi(
                recid=recjson['recid']
            )['doi'],
            existing_pid_checker=check_existing_pid,
        ),
        # Post process generated recjson according to needs in ZENODO
        process_sip(),
        # Generate MARC based on recjson structure
        finalize_record_sip(),
        # Seal the SIP and write MARCXML file and call bibupload on it
        upload_record_sip(),
        # Schedule background tasks.
        run_tasks(),
    ]
    name = "Upload"
    name_plural = "Uploads"
    enabled = True
    default = True
    api = True
    draft_definitions = {
        '_default': forms['ZenodoForm'],
    }

    marshal_deposition_fields = DepositionType.marshal_deposition_fields.copy()
    del marshal_deposition_fields['drafts']

    marshal_draft_fields = DepositionType.marshal_draft_fields.copy()
    del marshal_draft_fields['id']
    del marshal_draft_fields['completed']

    @classmethod
    def marshal_deposition(cls, deposition):
        """
        Generate a JSON representation for REST API of a Deposition
        """
        draft = deposition.get_or_create_draft('_default')
        obj = marshal(deposition, cls.marshal_deposition_fields)
        obj['metadata'] = draft.values

        # Add record and DOI information from latest SIP
        for sip in deposition.sips:
            if sip.is_sealed():
                obj['submitted'] = UTCISODateTimeString().format(sip.timestamp)
                recjson = sip.metadata
                if recjson.get('recid'):
                    obj['record_id'] = fields.Integer().format(
                        recjson.get('recid')
                    )
                    obj['record_url'] = fields.String().format(url_for(
                        'record.metadata',
                        recid=recjson.get('recid'),
                        _external=True
                    ))
                if recjson.get('doi') and \
                   recjson.get('doi').startswith(CFG_DATACITE_DOI_PREFIX+"/"):
                    obj['doi'] = fields.String().format(recjson.get('doi'))
                    obj['doi_url'] = fields.String().format(
                        "http://dx.doi.org/%s" % obj['doi']
                    )
                break

        return obj

    @classmethod
    def marshal_draft(cls, obj):
        """
        Generate a JSON representation for REST API of a DepositionDraft
        """
        return marshal(obj, cls.marshal_draft_fields)

    @classmethod
    def api_action(cls, deposition, action_id):
        if action_id == 'publish':
            return deposition.run_workflow(headless=True)
        raise InvalidApiAction(action_id)

    @classmethod
    def render_completed(cls, d):
        """
        Render page when deposition was successfully completed
        """
        ctx = dict(
            deposition=d,
            deposition_type=(
                None if d.type.is_default() else d.type.get_identifier()
            ),
            uuid=d.id,
            my_depositions=Deposition.get_depositions(
                current_user, type=d.type
            ),
            sip=d.get_latest_sip(),
            format_record=format_record,
        )

        return render_template('webdeposit_completed.html', **ctx)
