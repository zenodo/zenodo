# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from __future__ import absolute_import

from celery import chain
from celery.utils.log import get_task_logger

import os
import re
from tempfile import mkstemp
import time

from invenio.legacy.bibdocfile.api import BibDoc, BibRecDocs, \
    InvenioBibDocFileError
from invenio.modules.formatter import format_record
from invenio.legacy.bibrecord import record_add_field, record_xml_output
from invenio.legacy.bibsched.bibtask import task_low_level_submission
from invenio.modules.records.api import get_record
from invenio.celery import celery
from invenio.config import CFG_TMPSHAREDDIR, CFG_DATACITE_SITE_URL, \
    CFG_SITE_SUPPORT_EMAIL, CFG_SITE_NAME
from invenio.utils.mail import send_email
from invenio.legacy.dbquery import run_sql
from invenio.ext.logging.wrappers import register_exception
from invenio.legacy.search_engine import search_pattern, get_fieldvalues
from invenio.legacy.websubmit.icon_creator import create_icon, \
    InvenioWebSubmitIconCreatorError
from invenio.modules.pidstore.models import PersistentIdentifier
from invenio.modules.communities.models import Community
from invenio.ext.template import render_template_to_string


try:
    from altmetric import Altmetric, AltmetricHTTPException
except ImportError, e:
    register_exception(
        prefix='Altmetric module not installed: %s' % str(e),
        alert_admin=False
    )


# Setup logger
logger = get_task_logger(__name__)


ICON_SIZE = "90"
ICON_SUBFORMAT = 'icon-%s' % ICON_SIZE
ICON_FILEFORMAT = "png"
MAX_RECORDS = 100


def open_temp_file(prefix):
    """
    Create a temporary file to write MARC XML in
    """
    # Prepare to save results in a tmp file
    (fd, filename) = mkstemp(
        dir=CFG_TMPSHAREDDIR,
        prefix='prefix_' + time.strftime("%Y%m%d_%H%M%S_", time.localtime())
    )
    file_out = os.fdopen(fd, "w")
    logger.debug("Created temporary file %s" % filename)

    return (file_out, filename)


def bibupload(record=None, collection=None, file_prefix="", mode="-c"):
    """
    General purpose function that will write a MARCXML file and call bibupload
    on it.
    """
    if collection is None and record is None:
        return

    (file_out, filename) = open_temp_file(file_prefix)

    if collection is not None:
        file_out.write("<collection>")
        tot = 0
        for rec in collection:
            file_out.write(record_xml_output(rec))
            tot += 1
            if tot == MAX_RECORDS:
                file_out.write("</collection>")
                file_out.close()
                logger.debug("Submitting bibupload %s -n %s" % (mode, filename))
                task_low_level_submission('bibupload', 'openaire', mode, filename, '-n')

                (file_out, filename) = open_temp_file(file_prefix)
                file_out.write("<collection>")
                tot = 0
        file_out.write("</collection>")
    elif record is not None:
        tot = 1
        file_out.write(record_xml_output(record))

    file_out.close()
    if tot > 0:
        logger.debug("Submitting bibupload %s -n %s" % (mode, filename))
        task_low_level_submission('bibupload', 'openaire', mode, filename, '-n')


#
# Tasks
#
@celery.task(ignore_result=True)
def openaire_create_icon(docid=None, recid=None, reformat=True):
    """
    Celery task to create an icon for all documents in a given record or for
    just a specific document.
    """
    if recid:
        docs = BibRecDocs(recid).list_bibdocs()
    else:
        docs = [BibDoc(docid)]

    # Celery task will fail if BibDoc does not exists (on purpose ;-)
    for d in docs:
        logger.debug("Checking document %s" % d)
        if not d.get_icon(subformat_re=re.compile(ICON_SUBFORMAT)):
            logger.debug("Document has no icon")
            for f in d.list_latest_files():
                logger.debug("Checking file %s" % f)
                if not f.is_icon():
                    logger.debug("File not an icon")
                    file_path = f.get_full_path()
                    icon_path = None
                    try:
                        filename = os.path.splitext(
                            os.path.basename(file_path)
                        )[0]
                        logger.info("Creating icon from file %s" % file_path)
                        (icon_dir, icon_name) = create_icon(
                            {'input-file': file_path,
                             'icon-name': "icon-%s" % filename,
                             'multipage-icon': False,
                             'multipage-icon-delay': 0,
                             'icon-scale': ICON_SIZE,
                             'icon-file-format': ICON_FILEFORMAT,
                             'verbosity': 0})
                        icon_path = os.path.join(icon_dir, icon_name)
                    except InvenioWebSubmitIconCreatorError, e:
                        logger.warning('Icon for file %s could not be created: %s' % (file_path, str(e)))
                        register_exception(
                            prefix='Icon for file %s could not be created: %s' % (file_path, str(e)),
                            alert_admin=False
                        )

                    try:
                        if icon_path and os.path.exists(icon_path):
                            logger.debug("Adding icon %s to document" % icon_path)
                            d.add_icon(icon_path, subformat=ICON_SUBFORMAT)
                            recid_list = ",".join([str(x['recid']) for x in d.bibrec_links])
                            if reformat:
                                task_low_level_submission('bibreformat', 'openaire', '-i', recid_list)

                    except InvenioBibDocFileError, e:
                        logger.warning('Icon %s for file %s could not be added to document: %s' % (icon_path, f, str(e)))
                        register_exception(
                            prefix='Icon %s for file %s could not be added to document: %s' % (icon_path, f, str(e)),
                            alert_admin=False
                        )


@celery.task(ignore_result=True)
def openaire_check_icons():
    """
    Task to run a check of documents with out icons.
    """
    docs = run_sql("""
        SELECT f.id_bibdoc
        FROM bibdocfsinfo AS f
        LEFT OUTER JOIN (
            SELECT DISTINCT id_bibdoc, 1
            FROM bibdocfsinfo
            WHERE format LIKE '%;icon' AND last_version=1
        ) AS i ON i.id_bibdoc=f.id_bibdoc
        WHERE i.id_bibdoc is null
    """)

    for docid, in docs:
        openaire_create_icon.delay(docid=docid, reformat=False)


@celery.task(ignore_result=True)
def openaire_altmetric_check_all():
    """
    Retrieve Altmetric information for all records
    """
    # Records with DOI
    recids = search_pattern(p="0->Z", f="0247_a")

    # Do not parallelize tasks to not overload Altmetric
    subtasks = []
    logger.debug("Checking Altmetric for %s records" % len(recids))
    for i in xrange(0, len(recids), MAX_RECORDS):
        # Creating immutable subtasks - see http://docs.celeryproject.org/en/latest/userguide/canvas.html
        subtasks.append(openaire_altmetric_update.si(list(recids[i:i+MAX_RECORDS])))

    chain(*subtasks).apply_async()


@celery.task(ignore_result=True)
def openaire_altmetric_update(recids, upload=True):
    """
    Retrieve Altmetric information for a record.
    """
    logger.debug("Checking Altmetric for recids %s" % recids)
    a = Altmetric()

    records = []
    for recid in recids:
        logger.debug("Checking Altmetric for recid %s" % recid)
        try:
            # Check if we already have an Altmetric id
            sysno_inst = get_fieldvalues(recid, "035__9")
            if ['Altmetric'] in sysno_inst:
                continue

            doi_val = get_fieldvalues(recid, "0247_a")[0]
            logger.debug("Found DOI %s" % doi_val)
            json_res = a.doi(doi_val)
            logger.debug("Altmetric response: %s" % json_res)

            rec = {}
            record_add_field(rec, "001", controlfield_value=str(recid))

            if json_res:
                record_add_field(rec, '035', subfields=[
                    ('a', str(json_res['altmetric_id'])),
                    ('9', 'Altmetric')
                ])
                records.append(rec)
        except AltmetricHTTPException, e:
            logger.warning('Altmetric error for recid %s with DOI %s (status code %s): %s' % (recid, doi_val, e.status_code, str(e)))
            register_exception(
                prefix='Altmetric error (status code %s): %s' % (e.status_code, str(e)),
                alert_admin=False
            )
        except IndexError:
            logger.debug("No DOI found")
            pass

    if upload and records:
        if len(records) == 1:
            bibupload(record=records[0], file_prefix="altmetric")
        else:
            bibupload(collection=records, file_prefix="altmetric")

    return records


@celery.task(ignore_result=True, max_retries=6, default_retry_delay=10*60)
def openaire_update_doi(recid):
    """
    Update DOI in DataCite

    If it fails, it will retry every 10 minutes for 1 hour.
    """
    doi_val = get_fieldvalues(recid, "0247_a")[0]
    logger.debug("Found DOI %s in record %s" % (doi_val, recid))

    pid = PersistentIdentifier.get("doi", doi_val)
    if not pid:
        logger.debug("DOI not locally managed.")
        return
    else:
        logger.debug("DOI locally managed.")

    if not pid.has_object("rec", recid):
        raise Exception("DOI %s is not assigned to record %s." % (doi_val, recid))

    if pid.is_registered() or pid.is_deleted():
        logger.info("Updating DOI %s for record %s" % (doi_val, recid))

        url = "%s/record/%s" % (CFG_DATACITE_SITE_URL, recid)
        doc = format_record(recid, 'dcite')

        if not pid.update(url=url, doc=doc):
            m = "Failed to update DOI %s" % doi_val
            logger.error(m + "\n%s\n%s" % (url, doc))
            if not openaire_update_doi.request.is_eager:
                raise openaire_update_doi.retry(exc=Exception(m))
        else:
            logger.info("Successfully updated DOI %s." % doi_val)


@celery.task(ignore_result=True, max_retries=6, default_retry_delay=10*60)
def openaire_delete_doi(recid):
    """
    Delete DOI in DataCite

    If it fails, it will retry every 10 minutes for 1 hour.
    """
    doi_val = get_fieldvalues(recid, "0247_a")[0]
    logger.debug("Found DOI %s in record %s" % (doi_val, recid))

    pid = PersistentIdentifier.get("doi", doi_val)
    if not pid:
        logger.debug("DOI not locally managed.")
        return
    else:
        logger.debug("DOI locally managed.")

    if not pid.has_object("rec", recid):
        raise Exception("DOI %s is not assigned to record %s." % (doi_val, recid))

    if pid.is_registered():
        logger.info("Inactivating DOI %s for record %s" % (doi_val, recid))

        if not pid.delete():
            m = "Failed to inactive DOI %s" % doi_val
            logger.error(m)
            if not openaire_delete_doi.request.is_eager:
                raise openaire_delete_doi.retry(exc=Exception(m))
        else:
            logger.info("Successfully inactivated DOI %s." % doi_val)


@celery.task(ignore_result=True, max_retries=6, default_retry_delay=10*60)
def openaire_register_doi(recid):
    """
    Register a DOI for new publication

    If it fails, it will retry every 10 minutes for 1 hour.
    """
    doi_val = get_fieldvalues(recid, "0247_a")[0]
    logger.debug("Found DOI %s in record %s" % (doi_val, recid))

    pid = PersistentIdentifier.get("doi", doi_val)
    if not pid:
        logger.debug("DOI not locally managed.")
        return
    else:
        logger.debug("DOI locally managed.")

    if not pid.has_object("rec", recid):
        raise Exception("DOI %s is not assigned to record %s." % (doi_val, recid))

    if pid.is_new() or pid.is_reserved():
        logger.info("Registering DOI %s for record %s" % (doi_val, recid))

        url = "%s/record/%s" % (CFG_DATACITE_SITE_URL, recid)
        doc = format_record(recid, 'dcite')

        if not pid.register(url=url, doc=doc):
            m = "Failed to register DOI %s" % doi_val
            logger.error(m + "\n%s\n%s" % (url, doc))
            if not openaire_register_doi.request.is_eager:
                raise openaire_register_doi.retry(exc=Exception(m))
        else:
            logger.info("Successfully registered DOI %s." % doi_val)


@celery.task(ignore_result=True)
def openaire_upload_notification(recid):
    """
    Send a notification to all user collections.
    """
    ctx = {
        'record': get_record(recid),
    }

    ucolls = Community.from_recid(recid, provisional=True)
    for c in ucolls:
        try:
            if c.owner.email:
                ctx.update({
                    'community': c,
                })
                content = render_template_to_string("communities/new_upload_email.html", **ctx)
                send_email(CFG_SITE_SUPPORT_EMAIL, c.owner.email.encode('utf8'), "[%s] New upload to %s" % (CFG_SITE_NAME, c.title.encode('utf8')), content=content.encode('utf8'))
                logger.info("Sent email for new record %s to %s." % (recid, c.owner.email.encode('utf8')))
        except AttributeError:
            pass
