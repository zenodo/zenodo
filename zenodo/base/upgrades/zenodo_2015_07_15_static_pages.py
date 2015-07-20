# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import warnings
from sqlalchemy import *
from invenio.ext.sqlalchemy import db
from invenio.modules.upgrader.api import op
from invenio.utils.text import wait_for_user


depends_on = [u'zenodo_2015_06_24_new_type_lessons']

from invenio.modules.pages.models import Page

def info():
    return "Re-adds static pages as pages in the pages modul module."


def do_upgrade():
    """Implement your upgrades here."""
    # content starts at l74

    pgs = [
            ['about', pc_about],
            ['faq', pc_faq],
            ['terms', pc_terms],
            ['use-data', pc_use_data],
            ['deposit-data', pc_use_data],
            ['privacy', pc_privacy],
            ['policies', pc_policies],
            ['contact', pc_contact],
            ['support', pc_contact],
            ['features', pc_features],
            ['dev', pc_api]
          ]

    for pg in pgs:
        add_page(pg[0], pg[1])
    pass

def add_page(title, content, template='pages/default.html'):
    tp = Page()
    # set url to '/$title' with 'title' in lowercase'
    tp.url = "/{}".format(title.lower())
    tp.template_name = template
    db.session.add(tp)
    db.session.commit()

def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1


def pre_upgrade():
    """Run pre-upgrade checks (optional)."""
    # Example of raising errors:
    # raise RuntimeError("Description of error 1", "Description of error 2")


def post_upgrade():
    """Run post-upgrade checks (optional)."""
    # Example of issuing warnings:
    # warnings.warn("A continuable error occurred")

pc_contact = """
<h1>Contact</h1>

<p>
<strong>Support and general information</strong><br />
Email: <a href="mailto:info@zenodo.org">info@zenodo.org</a><br />
</p>
<p>
<strong>Questions related to European Commission funded research and OpenAIRE</strong><br />
OpenAIRE HelpDesk: <a href="http://www.openaire.eu/support/helpdesk">http://www.openaire.eu/support/helpdesk</a>
</p>

<p>
<strong>Frequently Asked Questions</strong><br />
Zenodo: <a href="/faq">http://zenodo.org/faq</a><br />
OpenAIRE and Open Access in general: <a href="http://www.openaire.eu/support/faq">http://www.openaire.eu/support/faq</a><br />
</p>

<p>
<strong>Address</strong><br />
European Organization for Nuclear Research<br />
CH-1211 CERN<br />
Genève 23<br />
Switzerland<br />
</p>
"""

pc_deposit_data = """
<div class="alert alert-danger"><strong>TODO:</strong> After first beta release</div>
<h1>Deposit data</h1>
"""

pc_use_data = """
<div class="alert alert-danger"><strong>TODO:</strong> After first beta release</div>
<h1>Use data</h1>
"""

pc_privacy = """
<div class="row">
    <div class="span12">
<h1>Privacy policy</h1>

<p>The Zenodo collaboration does not track, collect or retain personal information from users of Zenodo, except as otherwise provided herein.  In order to enhance Zenodo and monitor traffic, non-personal information such as IP addresses and cookies may be tracked and retained, as well as log files shared in aggregation with other community services (in particular OpenAIREplus partners). User provided information, like corrections of metadata or paper claims, will be integrated into the database without displaying its source and may shared with other services.</p>

<p>Zenodo will take all reasonable measures to protect the privacy of its users and to resist service interruptions, intentional attacks, or other events that may compromise the security of the Zenodo website.</p>

<p>If you have any questions about the Zenodo privacy policy, please contact <a href="mailto:info@zenodo.org">info@zenodo.org</a>.</p>
</div>
</div>
"""

pc_features = """
    <div class="jumbotron page-features" align="center">
        <h1>Introducing Zenodo!</h1>
    </div>


        <div class="features-page row" align="center">
                <div class="col-sm-4 col-md-4">
                <img class="img-circle hide" data-src="holder.js/140x140" alt="140x140" style="width: 140px; height: 140px;">
                  <h1>(All) Research.<br> Shared.</h1>
                  <h4>— your one stop research shop!</h4>
                  <p>All research outputs from across all fields of science are welcome! Zenodo accept any file format as well as both positive and negative results. However, we do promote peer-reviewed openly accessible research, and we do curate your upload before putting it on the front-page.</p>
                </div>
                <div class="col-sm-4 col-md-4">
                    <img class="img-circle hide" data-src="holder.js/140x140" alt="140x140" style="width: 140px; height: 140px;">
                  <h1>Citeable.<br>Discoverable.</h1>
                  <h4>— be found!</h4>
                  <p>Zenodo assigns all publicly available uploads a Digital Object Identifier (DOI) to make the upload easily and uniquely citeable. Zenodo further supports harvesting of all content via the OAI-PMH protocol.</p>
               </div>
               <div class="col-sm-4 col-md-4">
                  <img class="img-circle hide" data-src="holder.js/140x140" alt="140x140" style="width: 140px; height: 140px;">
                  <h1>Community<br>Collections</h1>
                  <h4>— create your own repository</h4>
                  <p>Zenodo allows you to create your own collection and accept or reject all uploads to it. Creating a space for your next workshop or project have never been easier. Plus, everything is citeable and discoverable.</p>
                </div>
        </div>
    </div>
<div class="marketing-bg">
    <div class="container">
    <div class="features-page row" align="center">

            <div class="col-sm-4 col-md-4">
                <img class="img-circle hide" data-src="holder.js/140x140" alt="140x140" style="width: 140px; height: 140px;">
              <h1>Safe</h1>
              <h4>— more than just a drop box!</h4>
              <p>Your research output is stored safely for the future in same cloud infrastructure as research data from CERN's <a href="http://home.web.cern.ch/about/accelerators/large-hadron-collider">Large Hadron Collider</a> using a CERN's battle-tested repository software <a href="http://invenio-software.org">INVENIO</a> used by some of the world's largest repositories such as <a href="http://inspirehep.net">INSPIRE HEP</a> and <a href="http://cds.cern.ch">CERN Document Server</a>.</p>
            </div>
            <div class="col-sm-4 col-md-4">
                <img class="img-circle hide" data-src="holder.js/140x140" alt="140x140" style="width: 140px; height: 140px;">
              <h1>Reporting</h1>
              <h4>— tell your funding agency!</h4>
              <p>Zenodo is integrated into reporting lines for research funded by the European Commission via <a href="http://www.openaire.eu">OpenAIRE</a>. Just upload your research on Zenodo and we will take care of the reporting for you. We plan to extend with futher funding agencies in the future so stay tuned!</p>
           </div>
           <div class="col-sm-4 col-md-4">
                <img class="img-circle hide" data-src="holder.js/140x140" alt="140x140" style="width: 140px; height: 140px;">
              <h1>Flexible<br>Licensing</h1>
              <h4>— not everything is under Creative Commons</h4>
              <p>Zenodo encourage you to share your research as openly as possible to maximize use and re-use of your research results. However, we also acknowledge that one size does not fit all, and therefore allow for uploading under a multitude of different licenses and access levels<super>*</super>.<br><small class="text-muted">* You are responsible for respecting applicable copyright and license conditions for the files you upload.</small></p>
            </div>
            <!--<div class="span4">
                <img class="img-circle" data-src="holder.js/140x140" alt="140x140" style="width: 140px; height: 140px;">
              <h1>Integration</h1>
              <h4>&mdash; upload straight from DropBox!</h4>
              <p>Already got your files in DropBox? Save your bandwidth and let Zenodo grab your uploads securely from your DropBox.</p>
            </div>-->
          </div>
</div>
</div>

    <div class="jumbotron page-features" align="center">
        <h1>Upcoming Features</h1>
    </div>
    <div class="container">
        <div class="features-page row" align="center">
            <div class="col-sm-4 col-md-4">
              <h1>Metadata Extraction</h1>
              <h4>— DRY, don't repeat yourself!</h4>
              <p>Zenodo will automatically discover basic information like title, description, authors and publication date about your upload so you just have to validate our findings instead of copy/pasting or re-typing everything.</p>
            </div>
            <div class="col-sm-4 col-md-4">
              <h1>Authentication</h1>
              <h4>— use your existing account.</h4>
              <p>Zenodo will allow authentication via other services such as Google, Twitter, ORCID and OpenAIRE, so that you do not have to remember yet another username and password for yet another service.</p>
           </div>
           <div class="col-sm-4 col-md-4">
              <h1>Your opinion...</h1>
              <h4>— tell us what to do!</h4>
              <p>We have tons of ideas for the future of Zenodo but your opinions, ideas and needs decide what we will work on, so give us your <a href="contact">feedback.</a></p>
           </div>
          </div>
    </div>
"""

pc_terms = """
<h1>Terms of use</h1>

<p>
Use of the Zenodo service (hereafter “Zenodo”) denotes agreement with the following terms:
</p>

<ol>
<li>Zenodo is provided free of charge for educational and informational use.</li>
<li>The contents of Zenodo will be updated or otherwise modified on a regular basis. Zenodo reserves the right to alter or delete information without notice.</li>
<li>All information is provided “as-is” and the user shall hold Zenodo and information providers supplying data to Zenodo free and harmless in connection with the use of such information.</li>
<li>Users shall respect copyright and applicable license conditions. In particular, reconstructing the fulltexts of articles from snippets is not allowed. Download and use of information from Zenodo does not amount to a transfer of intellectual property.</li>
<li>Information obtained from the metadata of the Zenodo collection specified here may be freely reused under the <a href="http://creativecommons.org/publicdomain/zero/1.0/">CC0</a> waiver unless explicitly specified otherwise. With the exception of email addresses whose bulk download is not allowed all metadata of the other Zenodo collections are available under the <a href="http://creativecommons.org/publicdomain/zero/1.0/">CC0</a> waiver.</li>
<li>Any use of Zenodo that interferes with its regular operations or violates these terms of use or applicable laws may, at the sole discretion of Zenodo, result in restriction or removal of user access.</li>
</ol>

<p>
Please contact <a href="mailto:info@zenodo.org">info@zenodo.org</a> if you have any questions or comments with respect to Zenodo; if you are unsure whether your intended use meets these terms; or, if you seek permission for use that does not fall within these terms.
</p>
"""


pc_policies = """
<h1>Policies</h1>
<div class="row">
<div class="col-md-6">
    <h4>Content</h4>
<dl>
<dt>Scope</dt>
<dd>All fields of science. All types of research artifacts. Content must not violate privacy or copyright, or breach confidentiality or non-disclosure for data collected from human subjects.</dd>

<dt>Status of research data</dt>
<dd>Any status is accepted, from any stage of the research lifecycle.</dd>

<dt>Eligible depositors</dt>
<dd>Anyone may register as user of Zenodo. All users are allowed to deposit content for which they possess the appropriate rights.</dd>

<dt>Ownership</dt>
<dd>By uploading content, no change of ownership is implied, and no property rights are transfer to CERN. All uploaded content remains the property of the parties prior to submission.</dd>

<dt>Versions</dt>
<dd>Data files are versioned. Records are not versioned. The uploaded data is archived as a Submission Information Package. Derivatives of data files are generated, but original content is never modified.
Records can be retracted from public view, however the data files and record is preserved.</dd>

<dt>Data file formats</dt>
<dd>All formats are allowed - even preservation unfriendly. We are working on guidelines and features that will help people deposit in preservation friendly formats.</dd>

<dt>Volume and size limitations</dt>
<dd>2GB per file size constraint. Higher quotas per file can be requested. Quotas are likely to be introduced at a later stage. All data files are stored in CERN Data Centres, primarily Geneva, with replicas in Budapest. Data files are kept in multiple replicas in a distributed file system which is backed up to tape on a nightly basis.</dd>

<dt>Data quality</dt>
<dd>All information is provided “as-is” and the user shall hold Zenodo and information providers supplying data to Zenodo free and harmless in connection with the use of such information.</dd>

</dl>

<h4>Withdrawal of data and revocation of DOIs</h4>
<dl>
<dt>Revocation</dt>
<dd>Content not considered to fall under the scope of the repository will be removed and associated DOIs issued by Zenodo revoked. Please signal promptly any suspected policy violation, ideally no later than 24 hours from upload. Alternatively, content found to already have an external DOI, will have the Zenodo DOI invalidated, and the record updated to indicate the original external DOI. User access may be revoked on violation of Terms of Use.</dd>

<dt>Withdrawal</dt>
<dd>If the uploaded research object must later be withdrawn, the reason for the withdrawal will be indicated on a tombstone page which will henceforth be served in its place. Withdrawal is considered an exceptional action which normally should be requested and fully justified by the original uploader. In any other circumstance reasonable attempts will be made to contact the original uploader to obtain consent. The DOI and the URL of the original object are retained.</dd>
</dl>

</div>

<div class="col-md-6">
<h4>Metadata</h4>

<dl>
<dt>Metadata access</dt>
<dd>Zenodo is provided free of charge for educational and informational use.
Metadata is licensed under CC0, except for email addresses.</dd>

<dt>Metadata reuse</dt>
<dd>Metadata is licensed under CC0, except for email addresses.
All metadata is exported via OAI-PMH and can be harvested.</dd>

<dt>Metadata types and sources</dt>
<dd>All metadata is stored internally in MARC according to the schema defined in <a href="http://invenio-software.org/wiki/Project/OpenAIREplus/DevelopmentRecordMarkup">http://invenio-software.org/wiki/Project/OpenAIREplus/DevelopmentRecordMarkup</a>. Metadata is exported in several standard formats such as MARCXML, Dublin Core and DataCite Metadata Schema according to OpenAIRE Guidelines.</dd>

<dt>Language</dt>
<dd>For textual items, English is preferred, but all languages accepted.</dd>

<dt>Embargo status</dt>
<dd>Users may deposit content under an embargo status and provide and end date for the embargo. The repository will initially restrict access to the data, and then automatically make the content publicly available after the end of the embargo period. User may deposit restricted data files, which will not be made publicly available.</dd>

<dt>Licenses</dt>
<dd>Users must specify a license for all publicly available files. User may specify a license for all closed access files.</dd>

<!--
<dt>Moderation by repository</dt>
<dd>All content is checked after upload by repository staff. Content not considered to fall under the scope of the repository will be removed, and the depositor notified. Content will also be removed in case of (but not excluded to) copyright violation, legal requirements and proven violations, national security and confidentiality concerns. All records are assigned a Digital Object Identifier. User access may be revoked on violation of Terms of Use.
</dd>
-->

</dl>



    <h4>Access and reuse of data</h4>
<dl>

<dt>Access to data objects</dt>
<dd>Files may be deposited under closed, open, or embargoed access. Data files deposited under closed access are protected against unauthorized access at all levels. Access to metadata and data files is provided over standard protocols such as HTTP and OAI-PMH.</dd>

<dt>Use and re-use of data objects</dt>
<dd>Use and re-use is subject to the license under which the data objects were deposited.</dd>

<dt>Tracking users and statistics</dt>
<dd>Zenodo does not track, collect or retain personal information from users of Zenodo, except as otherwise provided herein. In order to enhance Zenodo and monitor traffic, non-personal information such as IP addresses and cookies may be tracked and retained, as well as log files shared in aggregation with other community services (in particular OpenAIREplus partners). User provided information, like corrections of metadata or paper claims, will be integrated into the database without displaying its source and may be shared with other services.
Zenodo will take all reasonable measures to protect the privacy of its users and to resist service interruptions, intentional attacks, or other events that may compromise the security of the Zenodo website.</dd>
</dl>

<h4>Preservation of data</h4>
<dl>

<dt>Retention period</dt>
<dd>Items will be retained for the lifetime of the repository, which is currently the lifetime of the host laboratory CERN, which currently has an experimental programme defined for the next 20 years at least.</dd>

<dt>Functional preservation</dt>
<dd>Zenodo makes no promises of usability and understandability of deposited objects over time.</dd>

<dt>File preservation</dt>
<dd>Data files and metadata is backed up on a nightly basis, as well as replicated in multiple copies in the online system.</dd>

<dt>Fixity and authenticity</dt>
<dd>All data files are stored along with a MD5 checksum of the file content. Regular checks of files against their checksums are made.</dd>
</dl>

<h4>Succession plans</h4>
<dl>
<dd>In case of closure of the repository, best efforts will be made to integrate all content into suitable alternative institutional and/or subject based repositories.</dd>
</dl>
</div>
</div>





"""

pc_faq = """
<h1>FAQ</h1>

<p>See also <a href="http://www.openaire.eu/support/faq">OpenAIRE FAQ</a> for general information on Open Access and European Commission funded research.</p>

<div class="row">
    <div class="col-md-6">
<ul>

    <li>
        <h5>What is the maximum file size I can upload?</h5>
        <p>We currently accept files up to 2GB. If you would like to upload larger files, please <a href="contact">contact us</a>, and we will do our best to help you.</p>
    </li>
    <li>
        <h5>What are the size limits in Zenodo?</h5>
        <p>Currently there's a per file size limit of 2GB (you can have several 2GB files per dataset) and no limit on communities. Since we target the long-tail of science, we want this slice to be always free. We don’t want to turn away larger use cases either, but naturally we cant offer infinite space for free (!) so there must be a ceiling to this free slice, above which we will introduce paid for slices according to the business model developed within the sustainability plan. N.b. The current infrastructure has been tested with 10GB files, so possibly we can also raise the file limit either per community or for the whole of Zenodo if needed.</p>
    </li>
    <li>
        <h5>What can I upload?</h5>
        <p>All research outputs from all fields of science are welcome. In the upload form you can choose between types of files: publications (book, book section, conference paper, journal article, patent, preprint, report, thesis, technical note, working paper), posters, presentations, images (figures, plots, drawings, diagrams, photos) and videos/audio. We do check every piece of content being uploaded to ensure it is research related. Please see further information in our <a href="terms">Terms of Use</a> and <a href="policies">Policies</a>.</p>
    </li>
    <li>
        <h5>Is Zenodo only for EU-funded research?</h5>
        <p>No. We are open to all research outputs from all fields of science regardless of funding source. Given that Zenodo was launched within an EU funded project, the knowledge bases were first filled with EU project codes, but we are keen to extend this to other funders with your help.</p>
    </li>
    <li>
        <h5>How do you plan to secure ongoing funding for Zenodo?</h5>
        <p>Zenodo is still in its infancy, so whilst this is a good question to ask, we don’t have just one definitive answer since we are exploring several avenues as we mature the services. Zenodo was launched within the <a href="http://www.openaire.eu">OpenAIREplus</a> project as part of a European-wide research infrastructure. OpenAIREplus will deliver a sustainability plan for this infrastructure, with the optic of services for the future Horizon 2020 projects, and so this is definitely one possible funding source. Another possibility is CERN itself - Zenodo is developed and hosted by CERN in synergy with other large services running on the same software such as <a href="http://cds.cern.ch">CERN Document Server</a> and <a href="http://inspirehep.net">INSPIRE-HEP</a>. And CERN is familiar with large research datasets, managing the Large Hadron Collier data archive of 100 petabytes. Lastly Zenodo is developed on a fully open platform and, if found beneficial in a sustainability plan, could be migrated to a third party entity outside CERN. No matter which direction Zenodo will take, we are fully dedicated to delivering an open service and preserving your research for the future.</p>
    </li>
    <li>
        <h5>Is my data safe with you / What will happen to my uploads in the unlikely event that Zenodo has to close?</h5>
        <p>Yes, your data is stored in CERN Data Centre. Both data files and metadata is kept in multiple online replicas, as well as backed up to tape every night. CERN has considerable knowledge and experience in building and operating large scale digital repositories, and a commitment to maintain this data centre to collect and store 100s of PBs of LHC data as it grows over the next 20 years. In the highly unlikely event that Zenodo will have to close operations, we guarantee that we will migrate all content to other suitable repositories, and since all uploads have DOIs all citations and links to the dataset will not be affected.
        </p>
    </li>
    <li>
        <h5>What does it cost / Can we pay for Zenodo services? </h5>
        <p>Zenodo is free for the long tail of Science. In order to offer services to the more resource hungry research, we will introduce a ceiling to the free slice and offer paid for slices above, according to the business model developed within the sustainability plan. If you can't wait but immediately want to explore these paid for options, please <a href="/contact">contact us</a> and we will look at interim measures with you.</p>
    </li>
    <li>
        <h5>Really, who pays for this?</h5>
        <p>Zenodo is developed by <a href="http://www.cern.ch">CERN</a> under the EU FP7 project <a href="http://www.openaire.eu">OpenAIREplus</a> (grant agreement no. 283595).</p>
    </li>

</ul>
</div>
    <div class="col-md-6">
<ul>
    <li>
        <h5>Why is my upload not on the front-page?</h5>
        <p>All uploads go through a quick spam check by our staff prior to going on the front-page.</p>
    </li>
    <li>
        <h5>Why is my closed access upload not on the front-page?</h5>
        <p>Zenodo is a strong supporter of open data in all its forms (meaning data that anyone is free to use, reuse, and redistribute), and takes an incentives approach to encourage deposition under an open licence. We therefore only display Open Access uploads on the front-page. Your Closed Access upload is still discoverable through search queries, its DOI and community collections where it is included.</p>
    </li>
    <li>
        <h5>Why do you allow closed access uploads?</h5>
        <p>Zenodo is a strong supporter of open data in all its forms (meaning data that anyone is free to use, reuse, and redistribute), and takes an incentives approach to encourage deposition under an open licence. Since there isn't a unique way of licensing openly, and no consensus on the practice of adding attribution restrictions, we accept data under a variety of licences in order to be inclusive. We will however take an active lead in signalling the extra benefits of the most open licences, in terms of visibility and credit, and offer additional services and upload quotas on such data to encourage using them. This follows naturally from the publications policy of the <a href="http://www.openaire.eu">OpenAIRE initiative</a> which has been supporting Open Access throughout, but since it aims to gather all European Commission/European Research Area research results, it allows submission of the material which is not yet Open Access.</p>
    </li>
    <li>
        <h5>What happened to the OpenAIRE Orphan Record Repository?</h5>
        <p>OpenAIRE Orphan Record Repository got a make-over and was re-branded as Zenodo. If you happened to deposit your article in OpenAIRE Orphan Record Repository it is also available in Zenodo. You user account, was however not transferred to Zenodo, so you will have to <a href="/youraccount/register">register</a> again. If you register with the same email address in Zenodo as you used in OpenAIRE Orphan Record Repository, you will still have access to your publications. Don't hesitate to <a href="contact">contact us</a> for further information.</p>
    </li>
    <li>
        <h5>Where does the name come from?</h5>
        <p>Zenodo is derived from <a href="http://en.wikipedia.org/wiki/Zenodotus">Zenodotus</a>, the first librarian of the Ancient Library of Alexandria and father of the first recorded use of metadata, a landmark in library history.</p>
    </li>
    <li>
        <h5>How much storage do CERN have available?</h5>
        <p>Zenodo is currently a drop in the ocean. CERN currently stores more than 100PB of physics data from the <a href="http://home.web.cern.ch/about/accelerators/large-hadron-collider">Large Hadron Collider (LHC)</a>, and produces roughly 25PB per year when the LHC is running.</p>
    </li>

</ul>
</div>
</div>
"""

pc_about = """
<h1>About Zenodo</h1>

<div class="row">
    <div class="col-md-6 col-lg-7">
        <p>Zenodo builds and operate a simple and innovative service that enables researchers, scientists, EU projects and institutions to share and showcase multidisciplinary research results (data and publications) that are not part of the existing institutional or subject-based repositories of the research communities.</p>

<p>Zenodo enables researchers, scientists, EU projects and institutions to:</p>
<ul>
<li>easily share the long tail of small research results in a wide variety of formats including text, spreadsheets, audio, video, and images across all fields of science.</li>
<li>display their research results and get credited by making the research results citable and integrate them into existing reporting lines to funding agencies like the European Commission.</li>
<li>easily access and reuse shared research results.</li>
</ul>

<p><strong>Deliverables:</strong></p>
<ul>
    <li>An open digital repository for everyone and everything that isn’t served by a dedicated service; the so called “long tail” of research results.
    </li><li>A modern look and feel in line with current trends for state-of-the-art online services.</li>
    <li>Integration with OpenAIRE infrastructure, and assured inclusion in OpenAIRE corpus.</li>
    <li>Easy upload and semi-automatic metadata completion by communication with existing online services such as DropBox for upload, Mendeley/ORCID/CrossRef/OpenAIRE for upload and pre-filling metadata.</li>
    <li>Easy access to research results via innovative viewing and as well as open APIs and integration with existing online services and preservation of community independent data formats.</li>
    <li>A safe and trusted service by providing sound curation, archival and digital preservation strategies according to best practices.</li>
    <li>Persistent identifier minting (such as DOI) for shared research results.</li>
    <li>Service hosting according to industry best practices in CERN’s professional data centres.</li>
    <li>Easy means to link research results with other results, funding sources, institutes, and licenses.</li>
</ul>
    </div>
    <div class="col-md-6 col-lg-5">
        <div class="well"><h4>The name</h4>
        <p>Zenodo is derived from <a href="http://en.wikipedia.org/wiki/Zenodotus">Zenodotus</a>, the first librarian of the Ancient Library of Alexandria and father of the first recorded use of metadata, a landmark in library history.</p></div>

        <div class="well">
        <h4>Logo</h4>
<table class="table table-hover">
<thead>
<tr>
    <th></th>
    <th></th>
    <th>PNG</th>
    <th>JPEG</th>
</tr>
</thead>
<tbody>
<tr>
    <td>Color</td>
    <td><img class="img-rounded" src="img/logos/zenodo-gradient-200.png"></td>
    <td>
        <a href="img/logos/zenodo-gradient-2500.png">2500px</a><br>
        <a href="img/logos/zenodo-gradient-1000.png">1000px</a><br>
        <a href="img/logos/zenodo-gradient-200.png">200px</a><br>
    </td>
    <td>
        <a href="img/logos/zenodo-gradient-2500.jpg">2500px</a><br>
        <a href="img/logos/zenodo-gradient-1000.jpg">1000px</a><br>
        <a href="img/logos/zenodo-gradient-200.jpg">200px</a><br>
    </td>
</tr>
<tr>
    <td>Black</td>
    <td><img class="img-rounded" style="background-color: white;" src="img/logos/zenodo-black-200.png"></td>
    <td>
        <a href="img/logos/zenodo-black-2500.png">2500px</a><br>
        <a href="img/logos/zenodo-black-1000.png">1000px</a><br>
        <a href="img/logos/zenodo-black-200.png">200px</a><br>
    </td>
    <td>
        <small class="text-muted">Not available</small>
    </td>
</tr>
<tr>
    <td>White</td>
    <td><img class="img-rounded" style="background-color: #555555;" src="img/logos/zenodo-white-200.png"></td>
    <td>
        <a href="img/logos/zenodo-white-2500.png">2500px</a><br>
        <a href="img/logos/zenodo-white-1000.png">1000px</a><br>
        <a href="img/logos/zenodo-white-200.png">200px</a><br>
    </td>
    <td>
        <small class="text-muted">Not available</small>
    </td>
</tr>
</tbody>
</table>
        </div>
    </div>
</div>
"""

pc_api = """
<div class="row">
<div class="col-sm-3 col-md-3 hidden-print">
<ul class="nav nav-list well ">
  <li class="nav-header">API Documentation</li>
  <li><a href="#">Introduction</i></a></li>
  <li class="nav-header">REST API</li>
  <li><a href="#restapi-intro">Introduction</i></a></li>
  <li><a href="#restapi-quick">Quick start</i></a></li>
  <li><a href="#restapi-versioning">Versioning</i></a></li>
  <li><a href="#restapi-auth">Authentication</i></a></li>
  <li><a href="#restapi-requests">Requests</i></a></li>
  <li><a href="#restapi-responses">Responses</i></a></li>
  <li><a href="#restapi-http">HTTP status codes</i></a></li>
  <li><a href="#restapi-errors">Errors</i></a></li>
  <li><a href="#restapi-res">Resources</i></a></li>
  <li><a href="#restapi-res-dep"><i class="glyphicon glyphicon-chevron-right"></i> Depositions</i></a></li>
  <li><a href="#restapi-res-files"><i class="glyphicon glyphicon-chevron-right"></i> Deposition files</i></a></li>
  <li><a href="#restapi-res-actions"><i class="glyphicon glyphicon-chevron-right"></i> Deposition actions</i></a></li>
  <li><a href="#restapi-rep">Representations</i></a></li>
  <!--<li><a href="#restapi-faq">FAQ</i></a></li>-->
  <li><a href="#restapi-changes">Changes</i></a></li>
  <li class="nav-header">OAI-PMH API</li>
  <li><a href="#harvest-baseurl">Base URL</i></a></li>
  <li><a href="#harvest-metadata">Metadata formats</i></a></li>
  <li><a href="#harvest-sets">Sets</i></a></li>
  <li><a href="#harvest-schedule">Update schedule</i></a></li>
  <li><a href="#harvest-ratelimit">Rate limit</i></a></li>
  <li><a href="#harvest-changes">Changes</i></a></li>
  <!--<li class="nav-header">Metadata API</li>
  <li><a href="#metadata-url">URL structure</i></a></li>
  <li><a href="#metadata-metadata">Metadata formats</i></a></li>
  <li><a href="#metadata-changes">Changes</i></a></li>-->
</ul>
</div>
<div class="col-sm-9 col-md-9" data-spy="scroll" data-target=".navmenu">
<h1 id="intro"><strong>API Documentation</strong> <small>for developers</small></h1>
<hr />
Zenodo currently offers two different APIs:
<p>
<ul>
<li><strong>REST API</strong> &mdash; includes support for uploading your research outputs.</li>
<li><strong>OAI-PMH API</strong> &mdash; allows you to harvest all or parts of Zenodo via the OAI-PMH protocol.</li>
<!--<li><strong>Metadata API</strong> &mdash; machine readable records in several different formats.</li>-->
</ul>
</p>

<h2 id="restapi"><strong>REST API</strong> <small>upload your research outputs</small></h2><hr />
<h2 id="restapi-intro">Introduction</h2>
<p>The REST API allows you to programmatically upload and publish research outputs on Zenodo, with the same functionality which is available in our <a href="/deposit">Upload</a> user interface.</p>

<div class="panel-group dep-accord" id="dep-accord-0">
  <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-list0">
          <h4 id="restapi-res-">Quick start <small></small><span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-list0" class="panel-collapse collapse">
      <div style="padding: 9px 15px;">
          <p>This short guide will give a quick overview of how to upload and publish on Zenodo, and will be using Python together with the <a href="http://www.python-requests.org/en/latest/user/install/">Requests</a> package.</p>

<ol>

<li>
<p>First, make sure you have the <a href="http://www.python-requests.org/en/latest/user/install/">Requests</a> module installed:</p>
<pre>$ pip install requests</pre>
</li>

<li><p>Next, fire up a Python command prompt:</p>
<pre>$ python
Python 2.7.5+
[GCC 4.8.1] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>></pre>
</li>

<li><p>Import the <code>requests</code> and <code>json</code> modules (don't type the <code>>>></code>-part):</p>
<pre>>>> import requests
>>> import json</pre>
</li>

<li><p>Try to access the API:</p>
<pre>>>> r = requests.get("https://zenodo.org/api/deposit/depositions")
>>> r.status_code
401
>>> r.json()
{u'status': 401, u'message': u'Unauthorized'}
</pre>
</li>

<li>All API access requires an access token, so <a href="#restapi-auth">create</a> one.</li>

<li><p>Let's try again (replace <code>ACCESS_TOKEN</code> with your newly created personal access token):</p>
<pre>>>> r = requests.get("https://zenodo.org/api/deposit/depositions?access_token=ACCESS_TOKEN")
>>> r.status_code
200
>>> r.json()
[]</pre>
<p class="muted"><small>Note, if you already uploaded something, the output will be different.</small></p>
</li>

<li><p>Next, let's create a new empty upload:</p>
<pre>>>> headers = {"Content-Type": "application/json"}
>>> r = requests.post("https://zenodo.org/api/deposit/depositions?access_token=ACCESS_TOKEN", data="{}", headers=headers)
>>> r.status_code
201
>>> r.json()
{u'files': [], u'title': u'', u'created': u'2013-11-14T18:34:08+00:00', u'modified': u'2013-11-14T18:34:08+00:00', u'state': u'unsubmitted', u'owner': 1, u'id': 1234, u'metadata': {}}
>>> deposition_id = r.json()['id']
</pre>
</li>

<li><p>Now, let's upload a new file:</p>
<pre>>>> data = {'filename': 'myfirstfile.csv'}
>>> files = {'file': open('/path/to/myfirstfile.csv', 'rb')}
>>> r = requests.post("https://zenodo.org/api/deposit/depositions/%s/files?access_token=ACCESS_TOKEN" % deposition_id, data=data, files=files)
>>> r.status_code
201
>>> r.json()
{u'checksum': u'2b70e04bb31f2656ce967dc07103297f', u'filename': u'myfirstfile.csv', u'id': u'eb78d50b-ecd4-407a-9520-dfc7a9d1ab2c', u'filesize': u'27'}
</pre>
<p class="muted"><small>Maximum file size is 2GB per file.</small></p>
</li>

<li><p>Last thing missing, is just to add some metadata:</p>
<pre>
>>> data = {"metadata": {"title": "My first upload", "upload_type": "poster", "description": "This is my first upload", "creators": [{"name": "Doe, John", "affiliation": "Zenodo"}]}}
>>> r = requests.put("https://zenodo.org/api/deposit/depositions/%s?access_token=ACCESS_TOKEN" % deposition_id, data=json.dumps(data), headers=headers)
>>> r.status_code
200
</pre>
</li>

<li><p>and, we're ready to publish:</p>
<div class="alert alert-danger">Don't execute this last step - it will put your test upload straight online.</div>
<pre>
>>> r = requests.post("https://zenodo.org/api/deposit/depositions/%s/actions/publish?access_token=ACCESS_TOKEN" % deposition_id)
>>> r.status_code
202
</pre>
</li>
</ol>

      </div>
    </div>
  </div>
</div>



<h2 id="restapi-versioning">Versioning</h2>
<p>
The REST API is versioned. We strive not to make backward incompatible changes to the API, but if we do, we release a new version. <!-- By default our URL endpoint always provide the latest version. A client can force a specific API version by including the <code>X-API-Version</code> header in the request.</p>--> <a href="#restapi-changes">Changes</a> to the API are documented on this page, and advance notification is given on our <a href="http://twitter.com/zenodo_org">Twitter account</a>.</p>

<h2 id="restapi-auth">Authentication</h2>
<p>All API requests must be authenticated and over HTTPS. Any request over plain HTTP will fail. We support authentication with via OAuth 2.0.</p>

<p><strong>Acquiring a personal access token</strong>
<ol>
<li><a href="/youraccount/register">Register</a> for a Zenodo account if you don't already have one.</li>
<li>Go to your <a href="https://zenodo.org/account/settings/applications/">Applications</a>, to <a href="https://zenodo.org/account/settings/applications/tokens/new/">create a new token</a>.</li>
<li>Select the OAuth scopes you need (for the quick start tutorial you need <code>deposit:write</code> and <code>deposit:actions</code>).</li>
</ol>
</p>

<div class="alert alert-danger">
  <strong>Important!</strong> Do not share your personal access token with anyone else, and only use it over HTTPS.
</div>

<p><strong>Using access tokens</strong></p>
<p>A access token must be included in all requests as a URL parameter:</p>

<pre>
https://zenodo.org/api/deposit/depositions?access_token=ACCESS_TOKEN
</pre>

<p><strong>Scopes</strong></p>
Scopes assigns permissions to your access token to limit access to data and actions in Zenodo.

The following scopes exists:

<table class="table table-striped">
<thead>
<tr>
<th>Name</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>deposit:write</code></td>
<td>Grants write access to depositions, but does not allow publishing the upload.</td>
</tr>
<tr>
<td><code>deposit:actions</code></td>
<td>Grants access to publish, edit and discard edits for depositions.</td>
</tr>
</tbody>
</table>



<h2 id="restapi-requests">Requests</h2>
<p>The base URL of the API is <code>https://zenodo.org/api/</code>.</p>

<p>All <code>POST</code> and <code>PUT</code> request bodies must be JSON encoded, and must have content type of <code>application/json</code> unless specified otherwise in the specific resource (e.g. in the case of file uploads). The API will return a <code>415</code> error (see <a href="#restapi-http">HTTP status codes</a> and <a href="#restapi-errors">error responses</a>) if the wrong content type is provided.</p>


<h2 id="restapi-responses">Responses</h2>
<p>All response bodies are JSON encoded (UTF-8 encoded). A single resource is represented as a JSON
object:</p>
<pre>
{
    "field1": <em>value</em>,
    <em>...</em>
}
</pre>
<p>A collection of resources is represented as a JSON array of objects:</p>
<pre>
[
    {
        "field1": <em>value</em>,
        <em>...</em>
    },
    <em>...</em>
]
</pre>

<p>Timestamps are in UTC and formatted according to <a href="http://en.wikipedia.org/wiki/ISO_8601">ISO 8601</a>:</p>
<pre align="center">YYYY-MM-DDTHH:MM:SS+00:00</pre>

<h2 id="restapi-http">HTTP status codes</h2>
We use the following HTTP status codes to indicate success or failure of a request.

<table class="table table-striped">
<thead>
<tr>
<th>Code</th>
<th>Name</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>200</code></td>
<td>OK</td>
<td>Request succeeded. Response included. Usually sent for GET/PUT/PATCH requests.</td>
</tr>
<tr>
<td><code>201</code></td>
<td>Created</td>
<td>Request succeeded. Response included. Usually sent for POST requests.</td>
</tr>
<tr>
<td><code>202</code></td>
<td>Accepted</td>
<td>Request succeeded. Response included. Usually sent for POST requests, where background processing is needed to fulfill the request.</td>
</tr>
<tr>
<td><code>204</code></td>
<td>No Content</td>
<td>Request succeeded. No response included. Usually sent for DELETE requests.</td>
</tr>
<tr>
<td><code>400</code></td>
<td>Bad Request</td>
<td>Request failed. <a href="#restapi-errors">Error response</a> included.</td>
</tr>
<tr>
<td><code>401</code></td>
<td>Unauthorized</td>
<td>Request failed, due to an invalid access token. <a href="#restapi-errors">Error response</a> included.</td>
</tr>
<tr>
<td><code>403</code></td>
<td>Forbidden</td>
<td>Request failed, due to missing authorization (e.g. deleting an already submitted upload or missing scopes for your access token). <a href="#restapi-errors">Error response</a> included.
</td>
</tr>
<tr>
<td><code>404</code></td>
<td>Not Found</td>
<td>Request failed, due to the resource not being found. <a href="#restapi-errors">Error response</a> included.</td>
</tr>
<tr>
<td><code>405</code></td>
<td>Method Not Allowed</td>
<td>Request failed, due to unsupported HTTP method. <a href="#restapi-errors">Error response</a> included.</td>
</tr>
<tr>
<td><code>409</code></td>
<td>Conflict</td>
<td>Request failed, due to the current state of the resource (e.g. edit a deopsition which is not fully integrated). <a href="#restapi-errors">Error response</a> included.</td>
</tr>
<tr>
<td><code>415</code></td>
<td>Unsupported Media Type</td>
<td>Request failed, due to missing or invalid request header <code>Content-Type</code>. <a href="#restapi-errors">Error response</a> included.</td>
</tr>
<tr>
<td><code>429</code></td>
<td>Too Many Requests</td>
<td>Request failed, due to rate limiting. <a href="#restapi-errors">Error response</a> included.</td>
</tr>
<tr>
<td><code>500</code></td>
<td>Internal Server Error</td>
<td>Request failed, due to an internal server error. Error response <em>NOT</em> included. Don't worry, Zenodo admins have been notified and will be dealing with the problem ASAP.</td>
</tr>
</tbody>
</table>

<h2 id="restapi-errors">Errors</h2>
<p>
Error responses for 400 series errors (e.g. 400, 401, 403, ...) are returned as a JSON object with two attributes <code>message</code> and <code>status</code> (HTTP status code), and possibly an attribute <code>errors</code> with a list of more detailed errors.</p>

<p>Example of a simple error message without further detailed errors:</p>

<pre>
{
    "message": "Deposition not found",
    "status": 404
}
</pre>

<p>Example of an error message with additional detailed error messages:</p>

<pre>
{
    "message": "Validation error",
    "status": 400,
    "errors": [
        {"code": 10, "message":"Not a valid choice", "field": "access_right"}
    ]
}
</pre>
<p>The attribute <code>errors</code> is a JSON array of objects, with the attributes <code>message</code> and <code>code</code>, and possibly <code>field</code> for validation errors.</p>


<h2 id="restapi-res">Resources</h2>

<h3 id="restapi-res-dep">Depositions</h3>

<div class="panel-group dep-accord" id="dep-accord-1">
  <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-list">
          <h4 id="restapi-res-">List <small>GET deposit/depositions</small><span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-list" class="panel-collapse collapse">
      <div class="panel-body">
          <table class="table table-striped">
          <tbody>
          <tr>
              <th class="span2">Description</th>
              <td>List all depositions for the currently authenticated user</td>
          </tr>
          <tr>
              <th class="span2">URL</th>
              <td>https://zenodo.org/api/deposit/depositions</td>
          </tr>
          <tr>
              <th>Method</th>
              <td>GET</td>
          </tr>
          <tr>
              <th>Success response</th>
              <td><ul><li><strong>Code:</strong> <code>200 OK</code></li><li><strong>Body</strong>: an array of <a href="#restapi-rep-dep">deposition</a> resources.</li></ul></td>
          </tr>
          <tr>
              <th>Error response</th>
              <td>See <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</td>
          </tr>
          <tr>
              <th>Example</th>
              <td>
          <div class="tabbable">
            <ul class="nav nav-pills">
              <li class="active"><a href="#curl" data-toggle="tab">cURL</a></li>
              <li ><a href="#python" data-toggle="tab">Python</a></li>
            </ul>
            <div class="tab-content">
              <div class="tab-pane active" id="curl">
                <pre>$ curl -i https://zenodo.org/api/deposit/depositions/?access_token=ACCESS_TOKEN</pre>
              </div>
              <div class="tab-pane" id="python">
                <pre>import requests
response = requests.get("https://zenodo.org/api/deposit/depositions/?access_token=ACCESS_TOKEN")
print response.json()
                </pre>
              </div>
            </div>
          </div>
              </td>
          </tr>
          </tbody>
          </table>
      </div>
    </div>
  </div>
  <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-create">
        <h4 id="restapi-res-">Create <small>POST deposit/depositions</small><span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-create" class="panel-collapse collapse">
      <div class="panel-body">
<table class="table table-striped">
<tbody>
<tr>
    <th class="span2">Description</th>
    <td>Create a new deposition resource.</td>
</tr>
<tr>
    <th class="span2">URL</th>
    <td>https://zenodo.org/api/deposit/depositions</td>
</tr>
<tr>
    <th>Method</th>
    <td>POST</td>
</tr>
<tr>
    <th>Request headers</th>
    <td>Content-Type: application/json</td>
</tr>
<tr>
    <th>Scopes</th>
    <td><code>deposit:write</code></td>
</tr>
<tr>
    <th>Data parameters</th>
    <td><p>An empty JSON object <code>{}</code> or a <a href="#restapi-rep-meta">deposition metadata</a> resource. Example:</p>
    <pre>{
    "metadata": {
        "upload_type": "presentation",
        <em>...</em>
    }
}</pre></td>
</tr>
<tr>
    <th>Success response</th>
    <td><ul><li><strong>Code:</strong> <code>201 Created</code></li><li><strong>Body</strong>: a <a href="#restapi-rep-dep">deposition</a> resource.</li></ul></td>
</tr>
<tr>
    <th>Error response</th>
    <td>See <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</td>
</tr>
<tr>
    <th>Example</th>
    <td>
<div class="tabbable">
  <ul class="nav nav-pills">
    <li class="active"><a href="#curl-d-create" data-toggle="tab">cURL</a></li>
    <li ><a href="#python-d-create" data-toggle="tab">Python</a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="curl-d-create">
      <pre>$ curl -i -H "Content-Type: application/json" --data '{}' https://zenodo.org/api/deposit/depositions/?access_token=ACCESS_TOKEN

<em>or</em>

$ curl -i -H "Content-Type: application/json" -X POST --data '{"metadata": {"title": "My first upload", "upload_type": "poster", "description": "This is my first upload", "creators": [{"name": "Doe, John", "affiliation": "Zenodo"}]}}' https://zenodo.org/api/deposit/depositions/?access_token=ACCESS_TOKEN</pre>
    </div>
    <div class="tab-pane" id="python-d-create">
      <pre>import json
import requests

url = "https://zenodo.org/api/deposit/depositions/?access_token=ACCESS_TOKEN"
headers = {"Content-Type": "application/json"}
r = requests.post(url, data="{}", headers=headers)

<span class="muted"># or</span>

data = {"metadata": {"title": "My first upload", "upload_type": "poster", "description": "This is my first upload", "creators": [{"name": "Doe, John", "affiliation": "Zenodo"}]}}
r = requests.post(url, data=json.dumps(data), headers=headers)</pre>
    </div>
  </div>
</div>
    </td>
</tr>
</tbody>
</table>
      </div>
    </div>
  </div>
   <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-get">
          <h4 id="restapi-res-">Retrieve <small>GET deposit/depositions/:id</small><span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-get" class="panel-collapse collapse">
      <div class="panel-body">
          <table class="table table-striped">
<tbody>
<tr>
    <th class="span2">Description</th>
    <td>Retrieve a single deposition resource.</td>
</tr>
<tr>
    <th class="span2">URL</th>
    <td>https://zenodo.org/api/deposit/depositions/:id</td>
</tr>
<tr>
    <th>Method</th>
    <td>GET</td>
</tr>
<tr>
    <th>URL parameters</th>
    <td>
      <ul>
        <li><strong>Required:</strong>
          <ul>
            <li><strong>id:</strong> Deposition identifier</li>
          </ul>
        </li>
      </ul>
    </td>
</tr>
<tr>
    <th>Success response</th>
    <td><ul><li><strong>Code:</strong> <code>200 OK</code></li><li><strong>Body</strong>: a <a href="#restapi-rep-dep">deposition</a> resource.</li></ul></td>
</tr>
<tr>
    <th>Error response</th>
    <td>See <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</td>
</tr>
<tr>
    <th>Example</th>
    <td>
<div class="tabbable">
  <ul class="nav nav-pills">
    <li class="active"><a href="#curl-d-get" data-toggle="tab">cURL</a></li>
    <li ><a href="#python-d-get" data-toggle="tab">Python</a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="curl-d-get">
      <pre>$ curl -i https://zenodo.org/api/deposit/depositions/1234?access_token=ACCESS_TOKEN</pre>
    </div>
    <div class="tab-pane" id="python-d-get">
      <pre>import requests

r = requests.get("https://zenodo.org/api/deposit/depositions/1234?access_token=ACCESS_TOKEN")</pre>
    </div>
  </div>
</div>
    </td>
</tr>
</tbody>
</table>
      </div>
    </div>
  </div>
  <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-update">
          <h4 id="restapi-res-">Update <small>PUT deposit/depositions/:id</small><span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-update" class="panel-collapse collapse">
      <div class="panel-body">
        <table class="table table-striped">
<tbody>
<tr>
    <th class="span2">Description</th>
    <td>Update an existing deposition resource.</td>
</tr>
<tr>
    <th class="span2">URL</th>
    <td>https://zenodo.org/api/deposit/depositions/:id</td>
</tr>
<tr>
    <th>Method</th>
    <td>PUT</td>
</tr>
<tr>
    <th>Request headers</th>
    <td>Content-Type: application/json</td>
</tr>
<tr>
    <th>Scopes</th>
    <td><code>deposit:write</code></td>
</tr>
<tr>
    <th>URL parameters</th>
    <td>
      <ul>
        <li><strong>Required:</strong>
          <ul>
            <li><strong>id:</strong> Deposition identifier</li>
          </ul>
        </li>
      </ul>
    </td>
</tr>
<tr>
    <th>Data parameters</th>
    <td><p>A <a href="#restapi-rep-meta">deposition metadata</a> resource. Example:</p>
    <pre>{
    "metadata": {
        "upload_type": "presentation",
        <em>...</em>
    }
}</pre></td>
</tr>
<tr>
    <th>Success response</th>
    <td><ul><li><strong>Code:</strong> <code>200 OK</code></li><li><strong>Body</strong>: a <a href="#restapi-rep-dep">deposition</a> resource.</li></ul></td>
</tr>
<tr>
    <th>Error response</th>
    <td>See <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</td>
</tr>
<tr>
    <th>Example</th>
    <td>
<div class="tabbable">
  <ul class="nav nav-pills">
    <li class="active"><a href="#curl-d-put" data-toggle="tab">cURL</a></li>
    <li ><a href="#python-d-put" data-toggle="tab">Python</a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="curl-d-put">
      <pre>$ curl -i -H "Content-Type: application/json" -X PUT --data '{"metadata": {"title": "My first upload", "upload_type": "poster", "description": "This is my first upload", "creators": [{"name": "Doe, John", "affiliation": "Zenodo"}]}}' https://zenodo.org/api/deposit/depositions/1234?access_token=ACCESS_TOKEN</pre>
    </div>
    <div class="tab-pane" id="python-d-put">
      <pre>import json
import requests

url = "https://zenodo.org/api/deposit/depositions/1234?access_token=ACCESS_TOKEN"
headers = {"Content-Type": "application/json"}
data = {"metadata": {"title": "My first upload", "upload_type": "poster", "description": "This is my first upload", "creators": [{"name": "Doe, John", "affiliation": "Zenodo"}]}}

r = requests.put(url, data=json.dumps(data), headers=headers)</pre>
    </div>
  </div>
</div>
    </td>
</tr>
</tbody>
</table>
      </div>
    </div>
  </div>
  <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-delete">
          <h4 id="restapi-res-">Delete <small>DELETE deposit/depositions/:id</small><span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-delete" class="panel-collapse collapse">
      <div class="panel-body">
        <table class="table table-striped">
<tbody>
<tr>
    <th class="span2">Description</th>
    <td>Delete an existing deposition resource. Note, only unpublished depositions may be deleted.</td>
</tr>
<tr>
    <th class="span2">URL</th>
    <td>https://zenodo.org/api/deposit/depositions/:id</td>
</tr>
<tr>
    <th>Method</th>
    <td>DELETE</td>
</tr>
<tr>
    <th>Scopes</th>
    <td><code>deposit:write</code></td>
</tr>
<tr>
    <th>URL parameters</th>
    <td>
      <ul>
        <li><strong>Required:</strong>
          <ul>
            <li><strong>id:</strong> Deposition identifier</li>
          </ul>
        </li>
      </ul>
    </td>
</tr>
<tr>
    <th>Success response</th>
    <td><ul><li><strong>Code:</strong> <code>204 No Content</code></li><li><strong>Body</strong>: Empty.</li></ul></td>
</tr>
<tr>
    <th>Error response</th>
    <td>
    <ul>
    <li><code>404 Not found</code>: Deposition does not exist.</li>
      <li><code>403 Forbidden</code>: Deleting an already published deposition.</li>
    </ul>

    <p>See also <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</p>
    </td>
</tr>
<tr>
    <th>Example</th>
    <td>
<div class="tabbable">
  <ul class="nav nav-pills">
    <li class="active"><a href="#curl-d-del" data-toggle="tab">cURL</a></li>
    <li ><a href="#python-d-del" data-toggle="tab">Python</a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="curl-d-del">
      <pre>$ curl -i -X DELETE https://zenodo.org/api/deposit/depositions/1234?access_token=ACCESS_TOKEN</pre>
    </div>
    <div class="tab-pane" id="python-d-del">
      <pre>import requests

r = requests.delete("https://zenodo.org/api/deposit/depositions/1234?access_token=ACCESS_TOKEN")</pre>
    </div>
  </div>
</div>
    </td>
</tr>
</tbody>
</table>

      </div>
    </div>
  </div>
</div>






<h3 id="restapi-res-files">Deposition files</h3>

<div class="panel-group dep-accord">
  <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-f-list">
          <h4 id="restapi-res-">List <small>GET deposit/depositions/:id/files</small><span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-f-list" class="panel-collapse collapse">
      <div class="panel-body">
        <table class="table table-striped">
<tbody>
<tr>
    <th class="span2">Description</th>
    <td>List all deposition files for a given deposition.</td>
</tr>
<tr>
    <th class="span2">URL</th>
    <td>https://zenodo.org/api/deposit/depositions/:id/files</td>
</tr>
<tr>
    <th>Method</th>
    <td>GET</td>
</tr>
<tr>
    <th>URL parameters</th>
    <td>
      <ul>
        <li><strong>Required:</strong>
          <ul>
            <li><strong>id:</strong> Deposition identifier</li>
          </ul>
        </li>
      </ul>
    </td>
</tr>
<tr>
    <th>Success response</th>
    <td><ul><li><strong>Code:</strong> <code>200 OK</code></li><li><strong>Body</strong>: an array of <a href="#restapi-rep-files">deposition file</a> resources.</li></ul></td>
</tr>
<tr>
    <th>Error response</th>
    <td>See <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</td>
</tr>
<tr>
    <th>Example</th>
    <td>
<div class="tabbable">
  <ul class="nav nav-pills">
    <li class="active"><a href="#curl-f-list" data-toggle="tab">cURL</a></li>
    <li ><a href="#python-f-list" data-toggle="tab">Python</a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="curl-f-list">
      <pre>$ curl -i https://zenodo.org/api/deposit/depositions/1234/files?access_token=ACCESS_TOKEN</pre>
    </div>
    <div class="tab-pane" id="python-f-list">
      <pre>import requests

r = requests.get("https://zenodo.org/api/deposit/depositions/1234/files?access_token=ACCESS_TOKEN")</pre>
    </div>
  </div>
</div>
    </td>
</tr>
</tbody>
</table>
      </div>
    </div>
  </div>
  <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-f-create">
          <h4 id="restapi-res-">Create (upload) <small>POST deposit/depositions/:id/files</small><span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-f-create" class="panel-collapse collapse">
      <div class="panel-body">
        <table class="table table-striped">
<tbody>
<tr>
    <th class="span2">Description</th>
    <td>Upload a new file.</td>
</tr>
<tr>
    <th class="span2">URL</th>
    <td>https://zenodo.org/api/deposit/depositions/:id/files</td>
</tr>
<tr>
    <th>Method</th>
    <td>POST</td>
</tr>
<tr class="warning">
    <th>Request headers</th>
    <td>Content-Type: multipart/form-data</td>
</tr>
<tr>
    <th>Scopes</th>
    <td><code>deposit:write</code></td>
</tr>
<tr>
    <th>URL parameters</th>
    <td>
      <ul>
        <li><strong>Required:</strong>
          <ul>
            <li><strong>id:</strong> Deposition identifier</li>
          </ul>
        </li>
      </ul>
    </td>
</tr>
<tr>
    <th>Data parameters</th>
    <td></td>
</tr>
<tr>
    <th>Success response</th>
    <td><ul><li><strong>Code:</strong> <code>201 Created</code></li><li><strong>Body</strong>: a <a href="#restapi-rep-files">deposition file</a> resource.</li></ul></td>
</tr>
<tr>
    <th>Error response</th>
    <td>See <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</td>
</tr>
<tr>
    <th>Example</th>
    <td>
<div class="tabbable">
  <ul class="nav nav-pills">
    <li class="active"><a href="#curl-f-post" data-toggle="tab">cURL</a></li>
    <li ><a href="#python-f-post" data-toggle="tab">Python</a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="curl-f-post">
      <pre>$ curl -i -F name=myfirstfile.csv -F file=@path/to/local_file.csv https://zenodo.org/api/deposit/depositions/1234/files?access_token=ACCESS_TOKEN</pre>
    </div>
    <div class="tab-pane" id="python-f-post">
      <pre>import json
import requests

url = "https://zenodo.org/api/deposit/depositions/1234/files?access_token=ACCESS_TOKEN"
data = {'filename': 'myfirstfile.csv'}
files = {'file': open('path/to/local_file.csv', 'rb')}
r = requests.post(url, data=data, files=files)</pre>
    </div>
  </div>
</div>
    </td>
</tr>
</tbody>
</table>
      </div>
    </div>
  </div>
  <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-f-sort">
          <h4 id="restapi-res-">Sort <small>PUT deposit/depositions/:id/files</small><span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-f-sort" class="panel-collapse collapse">
      <div class="panel-body">
        <table class="table table-striped">
<tbody>
<tr>
    <th class="span2">Description</th>
    <td>Sort the files for a deposition. By default, the first file is shown in the file preview.</td>
</tr>
<tr>
    <th class="span2">URL</th>
    <td>https://zenodo.org/api/deposit/depositions/:id/files</td>
</tr>
<tr>
    <th>Method</th>
    <td>PUT</td>
</tr>
<tr>
    <th>Request headers</th>
    <td>Content-Type: application/json</td>
</tr>
<tr>
    <th>Scopes</th>
    <td><code>deposit:write</code></td>
</tr>
<tr>
    <th>URL parameters</th>
    <td>
      <ul>
        <li><strong>Required:</strong>
          <ul>
            <li><strong>id:</strong> Deposition identifier</li>
          </ul>
        </li>
      </ul>
    </td>
</tr>
<tr>
    <th>Data parameters</th>
    <td><p>A JSON array of partial <a href="#restapi-rep-files">deposition file</a> resources with only the <code>id</code> attribute. Example:</p>
    <pre>[
    {"id": "<em>&lt;file id 1&gt;</em>"},
    {"id": "<em>&lt;file id 2&gt;</em>"},
    <em>...</em>
]</pre></td>
</tr>
<tr>
    <th>Success response</th>
    <td><ul><li><strong>Code:</strong> <code>200 OK</code></li><li><strong>Body</strong>: an array of <a href="#restapi-rep-files">deposition file</a> resources.</li></ul></td>
</tr>
<tr>
    <th>Error response</th>
    <td>See <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</td>
</tr>
<tr>
    <th>Example</th>
    <td>
<div class="tabbable">
  <ul class="nav nav-pills">
    <li class="active"><a href="#curl-f-put" data-toggle="tab">cURL</a></li>
    <li ><a href="#python-f-put" data-toggle="tab">Python</a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="curl-f-put">
      <pre>$ curl -i -X PUT -H "Content-Type: application/json" --data '[{"id":"21fedcba-9876-5432-1fed-cba987654321"}, {"id":"12345678-9abc-def1-2345-6789abcdef12"}]' https://zenodo.org/api/deposit/depositions/1234/files?access_token=ACCESS_TOKEN
</pre>
    </div>
    <div class="tab-pane" id="python-f-put">
      <pre>import json
import requests

url = "https://zenodo.org/api/deposit/depositions/1234/files?access_token=ACCESS_TOKEN"
headers = {"Content-Type": "application/json"}
data = [{'id': '21fedcba-9876-5432-1fed-cba987654321'}, {'id': '12345678-9abc-def1-2345-6789abcdef12'}]

r = requests.put(url, data=json.dumps(data), headers=headers)</pre>
    </div>
  </div>
</div>
    </td>
</tr>
</tbody>
</table>
      </div>
    </div>
  </div>
  <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-f-get">
          <h4 id="restapi-res-">Retrieve <small>GET deposit/depositions/:id/files/:file_id</small> <span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-f-get" class="panel-collapse collapse">
      <div class="panel-body">
<table class="table table-striped">
<tbody>
<tr>
    <th class="span2">Description</th>
    <td>Retrieve a single deposition file.</td>
</tr>
<tr>
    <th class="span2">URL</th>
    <td>https://zenodo.org/api/deposit/depositions/:id/files/:file_id</td>
</tr>
<tr>
    <th>Method</th>
    <td>GET</td>
</tr>
<tr>
    <th>URL parameters</th>
    <td>
      <ul>
        <li><strong>Required:</strong>
          <ul>
            <li><strong>id:</strong> Deposition identifier</li>
            <li><strong>file_id:</strong> Deposition file identifier</li>
          </ul>
        </li>
      </ul>
    </td>
</tr>
<tr>
    <th>Success response</th>
    <td><ul><li><strong>Code:</strong> <code>200 OK</code></li><li><strong>Body</strong>: a <a href="#restapi-rep-files">deposition file</a> resource.</li></ul></td>
</tr>
<tr>
    <th>Error response</th>
    <td>See <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</td>
</tr>
<tr>
    <th>Example</th>
    <td>
<div class="tabbable">
  <ul class="nav nav-pills">
    <li class="active"><a href="#curl-f-get" data-toggle="tab">cURL</a></li>
    <li ><a href="#python-f-get" data-toggle="tab">Python</a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="curl-f-get">
      <pre>$ curl -i https://zenodo.org/api/deposit/depositions/1234/files/12345678-9abc-def1-2345-6789abcdef12?access_token=ACCESS_TOKEN</pre>
    </div>
    <div class="tab-pane" id="python-f-get">
      <pre>import requests

r = requests.get("https://zenodo.org/api/deposit/depositions/1234/files/12345678-9abc-def1-2345-6789abcdef12?access_token=ACCESS_TOKEN")</pre>
    </div>
  </div>
</div>
    </td>
</tr>
</tbody>
</table>
      </div>
    </div>
  </div>
  <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-f-update">
          <h4 id="#restapi-obj-deposition-file">Update <small>PUT deposit/depositions/:id/files/:file_id</small><span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-f-update" class="panel-collapse collapse">
      <div class="panel-body">
        <table class="table table-striped">
<tbody>
<tr>
    <th class="span2">Description</th>
    <td>Update a deposition file resource. Currently the only use is renaming an already uploaded file. If you one to replace the actual file, please delete the file and upload a new file.</td>
</tr>
<tr>
    <th class="span2">URL</th>
    <td>https://zenodo.org/api/deposit/depositions/:id/files/:file_id</td>
</tr>
<tr>
    <th>Method</th>
    <td>PUT</td>
</tr>
<tr>
    <th>Request headers</th>
    <td>Content-Type: application/json</td>
</tr>
<tr>
    <th>Scopes</th>
    <td><code>deposit:write</code></td>
</tr>
<tr>
    <th>URL parameters</th>
    <td>
      <ul>
        <li><strong>Required:</strong>
          <ul>
            <li><strong>id:</strong> Deposition identifier</li>
            <li><strong>file_id:</strong> Deposition file identifier</li>
          </ul>
        </li>
      </ul>
    </td>
</tr>
<tr>
    <th>Data parameters</th>
    <td><p>A partial <a href="#restapi-rep-files">deposition file</a> resources with only the <code>filename</code> attributes. Example:</p>
    <pre>{
    "filename": "<em>&lt;new name&gt;</em>"
}
</pre></td>
</tr>
<tr>
    <th>Success response</th>
    <td><ul><li><strong>Code:</strong> <code>200 OK</code></li><li><strong>Body</strong>: a <a href="#restapi-rep-files">deposition file</a> resource.</li></ul></td>
</tr>
<tr>
    <th>Error response</th>
    <td>See <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</td>
</tr>
<tr>
    <th>Example</th>
    <td>
<div class="tabbable">
  <ul class="nav nav-pills">
    <li class="active"><a href="#curl-f-put-1" data-toggle="tab">cURL</a></li>
    <li ><a href="#python-f-put-1" data-toggle="tab">Python</a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="curl-f-put-1">
      <pre>$ curl -i -X PUT -H "Content-Type: application/json" --data '{"filename": "someothername.csv"}' https://zenodo.org/api/deposit/depositions/1234/files/21fedcba-9876-5432-1fed-cba987654321?access_token=ACCESS_TOKEN</pre>
    </div>
    <div class="tab-pane" id="python-f-put-1">
      <pre>import json
import requests

url = "https://zenodo.org/api/deposit/depositions/1234/files/21fedcba-9876-5432-1fed-cba987654321?access_token=ACCESS_TOKEN"
headers = {"Content-Type": "application/json"}
data = {"filename": "someothername.csv"}

r = requests.put(url, data=json.dumps(data), headers=headers)</pre>
    </div>
  </div>
</div>
    </td>
</tr>
</tbody>
</table>
      </div>
    </div>
  </div>
  <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-f-delete">
          <h4 id="restapi-res-">Delete <small>DELETE deposit/depositions/:id/files/:file_id</small><span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-f-delete" class="panel-collapse collapse">
      <div class="panel-body">
        <table class="table table-striped">
<tbody>
<tr>
    <th class="span2">Description</th>
    <td>Delete an existing deposition file resource. Note, only deposition files for unpublished depositions may be deleted.</td>
</tr>
<tr>
    <th class="span2">URL</th>
    <td>https://zenodo.org/api/deposit/depositions/:id/files/:file_id</td>
</tr>
<tr>
    <th>Method</th>
    <td>DELETE</td>
</tr>
<tr>
    <th>Scopes</th>
    <td><code>deposit:write</code></td>
</tr>
<tr>
    <th>URL parameters</th>
    <td>
      <ul>
        <li><strong>Required:</strong>
          <ul>
            <li><strong>id:</strong> Deposition identifier</li>
            <li><strong>file_id:</strong> Deposition file identifier</li>
          </ul>
        </li>
      </ul>
    </td>
</tr>
<tr>
    <th>Success response</th>
    <td><ul><li><strong>Code:</strong> <code>204 No Content</code></li><li><strong>Body</strong>: Empty.</li></ul></td>
</tr>
<tr>
    <th>Error response</th>
    <td>
    <ul>
      <li><code>404 Not found</code>: Deposition file does not exist.</li>
      <li><code>403 Forbidden</code>: Deleting an already published deposition.</li>
    </ul>

    <p>See also <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</p>
    </td>
</tr>
<tr>
    <th>Example</th>
    <td>
<div class="tabbable">
  <ul class="nav nav-pills">
    <li class="active"><a href="#curl-f-del" data-toggle="tab">cURL</a></li>
    <li ><a href="#python-f-del" data-toggle="tab">Python</a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="curl-f-del">
      <pre>$ curl -i -X DELETE https://zenodo.org/api/deposit/depositions/1234/files/21fedcba-9876-5432-1fed-cba987654321?access_token=ACCESS_TOKEN</pre>
    </div>
    <div class="tab-pane" id="python-f-del">
      <pre>import requests

r = requests.delete("https://zenodo.org/api/deposit/depositions/1234/files/21fedcba-9876-5432-1fed-cba987654321?access_token=ACCESS_TOKEN")</pre>
    </div>
  </div>
</div>
    </td>
</tr>
</tbody>
</table>
      </div>
    </div>
  </div>
</div>


<h3 id="restapi-res-actions">Deposition actions</h3>


<div class="panel-group dep-accord">
<div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-a-publish">
          <h4 id="restapi-res-">Publish <small>POST deposit/depositions/:id/actions/publish</small> <span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-a-publish" class="panel-collapse collapse">
      <div class="panel-body">

<table class="table table-striped">
<tbody>
<tr>
    <th class="span2">Description</th>
    <td>Publish a deposition. Note, once a deposition is published, you can no longer delete it.</td>
</tr>
<tr>
    <th class="span2">URL</th>
    <td>https://zenodo.org/api/deposit/depositions/:id/actions/publish</td>
</tr>
<tr>
    <th>Method</th>
    <td>POST</td>
</tr>
<tr class="warning">
    <th>Request headers</th>
    <td><em>None</em></td>
</tr>
<tr>
    <th>Scopes</th>
    <td><code>deposit:actions</code></td>
</tr>
<tr>
    <th>URL parameters</th>
    <td>
      <ul>
        <li><strong>Required:</strong>
          <ul>
            <li><strong>id:</strong> Deposition identifier</li>
          </ul>
        </li>
      </ul>
    </td>
</tr>
<tr>
    <th>Success response</th>
    <td><ul><li><strong>Code:</strong> <code>202 Accepted</code></li><li><strong>Body</strong>: a <a href="#restapi-rep-dep">deposition</a> resource.</li></ul></td>
</tr>
<tr>
    <th>Error response</th>
    <td>See <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</td>
</tr>
<tr>
    <th>Example</th>
    <td>
<div class="tabbable">
  <ul class="nav nav-pills">
    <li class="active"><a href="#curl-a-pub" data-toggle="tab">cURL</a></li>
    <li ><a href="#python-a-pub" data-toggle="tab">Python</a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="curl-a-pub">
      <pre>$ curl -i -X POST https://zenodo.org/api/deposit/depositions/1234/actions/publish?access_token=ACCESS_TOKEN</pre>
    </div>
    <div class="tab-pane" id="python-a-pub">
      <pre>import requests

r = requests.post("https://zenodo.org/api/deposit/depositions/1234/actions/publish?access_token=ACCESS_TOKEN")</pre>
    </div>
  </div>
</div>
    </td>
</tr>
</tbody>
</table>
</div>
    </div>
  </div>




<div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-a-edit">
          <h4 id="restapi-a-edit">Edit <small>POST deposit/depositions/:id/actions/edit</small> <span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-a-edit" class="panel-collapse collapse">
      <div class="panel-body">

<table class="table table-striped">
<tbody>
<tr>
    <th class="span2">Description</th>
    <td>Unlock already submitted deposition for editing.</td>
</tr>
<tr>
    <th class="span2">URL</th>
    <td>https://zenodo.org/api/deposit/depositions/:id/actions/edit</td>
</tr>
<tr>
    <th>Method</th>
    <td>POST</td>
</tr>
<tr class="warning">
    <th>Request headers</th>
    <td><em>None</em></td>
</tr>
<tr>
    <th>Scopes</th>
    <td><code>deposit:actions</code></td>
</tr>
<tr>
    <th>URL parameters</th>
    <td>
      <ul>
        <li><strong>Required:</strong>
          <ul>
            <li><strong>id:</strong> Deposition identifier</li>
          </ul>
        </li>
      </ul>
    </td>
</tr>
<tr>
    <th>Success response</th>
    <td><ul><li><strong>Code:</strong> <code>201 Created</code></li><li><strong>Body</strong>: a <a href="#restapi-rep-dep">deposition</a> resource.</li></ul></td>
</tr>
<tr>
    <th>Error response</th>
    <td>
    <ul>
      <li><code>400 Bad Request</code>: Deposition state does not allow for editing (e.g. depositions in state <code>inprogress</code>).</li>
      <li><code>409 Conflict</code>: Deposition is in the process of being integrated, please wait 5 minutes before trying again.</li>
    </ul>
    See <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</td>
</tr>
<tr>
    <th>Example</th>
    <td>
<div class="tabbable">
  <ul class="nav nav-pills">
    <li class="active"><a href="#curl-a-edit" data-toggle="tab">cURL</a></li>
    <li ><a href="#python-a-edit" data-toggle="tab">Python</a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="curl-a-edit">
      <pre>$ curl -i -X POST https://zenodo.org/api/deposit/depositions/1234/actions/edit?access_token=ACCESS_TOKEN</pre>
    </div>
    <div class="tab-pane" id="python-a-edit">
      <pre>import requests

r = requests.post("https://zenodo.org/api/deposit/depositions/1234/actions/edit?access_token=ACCESS_TOKEN")</pre>
    </div>
  </div>
</div>
    </td>
</tr>
</tbody>
</table>
</div>
    </div>
  </div>




<div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-a-discard">
          <h4 id="restapi-a-discard">Discard <small>POST deposit/depositions/:id/actions/discard</small> <span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-a-discard" class="panel-collapse collapse">
      <div class="panel-body">

<table class="table table-striped">
<tbody>
<tr>
    <th class="span2">Description</th>
    <td>Discard changes in the current editing session.</td>
</tr>
<tr>
    <th class="span2">URL</th>
    <td>https://zenodo.org/api/deposit/depositions/:id/actions/discard</td>
</tr>
<tr>
    <th>Method</th>
    <td>POST</td>
</tr>
<tr class="warning">
    <th>Request headers</th>
    <td><em>None</em></td>
</tr>
<tr>
    <th>Scopes</th>
    <td><code>deposit:actions</code></td>
</tr>
<tr>
    <th>URL parameters</th>
    <td>
      <ul>
        <li><strong>Required:</strong>
          <ul>
            <li><strong>id:</strong> Deposition identifier</li>
          </ul>
        </li>
      </ul>
    </td>
</tr>
<tr>
    <th>Success response</th>
    <td><ul><li><strong>Code:</strong> <code>201 Created</code></li><li><strong>Body</strong>: a <a href="#restapi-rep-dep">deposition</a> resource.</li></ul></td>
</tr>
<tr>
    <th>Error response</th>
    <td>
    <ul>
      <li><code>400 Bad Request</code>: Deposition is not being edited.</li>
    </ul>
    See <a href="#restapi-http">HTTP status codes</a> (400 and 500 series errors) and <a href="#restapi-errors">error responses</a>.</td>
</tr>
<tr>
    <th>Example</th>
    <td>
<div class="tabbable">
  <ul class="nav nav-pills">
    <li class="active"><a href="#curl-a-discard" data-toggle="tab">cURL</a></li>
    <li ><a href="#python-a-discard" data-toggle="tab">Python</a></li>
  </ul>
  <div class="tab-content">
    <div class="tab-pane active" id="curl-a-discard">
      <pre>$ curl -i -X POST https://zenodo.org/api/deposit/depositions/1234/actions/discard?access_token=ACCESS_TOKEN</pre>
    </div>
    <div class="tab-pane" id="python-a-discard">
      <pre>import requests

r = requests.post("https://zenodo.org/api/deposit/depositions/1234/actions/discard?access_token=ACCESS_TOKEN")</pre>
    </div>
  </div>
</div>
    </td>
</tr>
</tbody>
</table>
</div>
    </div>
  </div>




</div>


<h2 id="restapi-rep">Representations</h2>

<p>The following section documents all the object attributes for the above documented resources.</p>

<div class="panel-group dep-accord">
<div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-r-dep">
          <h4 id="restapi-rep-dep">Deposition <small></small> <span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-r-dep" class="panel-collapse collapse">
      <div class="panel-body">
<table class="table table-striped">
<thead>
<tr>
  <th class="span2">Attribute</th>
  <th>Type</th>
  <th>Editable</th>
  <th>Description</th>
</tr>
</thead>
<tbody>
<tr>
    <td><code>created</code></td>
    <td>Timestamp</td>
    <td>No</td>
    <td>Creation time of deposition (in ISO8601 format).</td>
</tr>
<tr>
    <td><code>doi</code></td>
    <td>String</td>
    <td>No</td>
    <td>Digital Object Identifier (DOI). When you publish your deposition, we register a DOI in <a href="http://www.datacite.org">DataCite</a> for your upload, unless you manually provided us with one. This field is only present for published depositions.</td>
</tr>
<tr>
    <td><code>doi_url</code></td>
    <td>URL</td>
    <td>No</td>
    <td>Persistent link to your published deposition. This field is only present for published depositions.</td>
</tr>
<tr>
    <td><code>files</code></td>
    <td>Array</td>
    <td>Yes</td>
    <td>A list of <a href="#restapi-rep-files">deposition files</a> resources.</td>
</tr>
<tr>
    <td><code>id</code></td>
    <td>Integer</td>
    <td>No</td>
    <td>Deposition identifier</td>
</tr>
<tr>
    <td><code>metadata</code></td>
    <td>Object</td>
    <td>Yes</td>
    <td>A <a href="#restapi-rep-meta">deposition metadata</a> resource</td>
</tr>
<tr>
    <td><code>modified</code></td>
    <td>Timestamp</td>
    <td>No</td>
    <td>Last modification time of deposition (in ISO8601 format).</td>
</tr>
<tr>
    <td><code>owner</code></td>
    <td>Integer</td>
    <td>No</td>
    <td>User identifier of the owner of the deposition.</td>
</tr>
<tr>
    <td><code>record_id</code></td>
    <td>Integer</td>
    <td>No</td>
    <td>Record identifier.  This field is only present for published depositions.</td>
</tr>
<tr>
    <td><code>record_url</code></td>
    <td>URL</td>
    <td>No</td>
    <td>URL to public version of record for this deposition. This field is only present for published depositions.</td>
</tr>
<tr>
    <td><code>state</code></td>
    <td>String</td>
    <td>No</td>
    <td>One of the values:<ul>
      <li><code>"inprogress"</code>: Deposition metadata can be updated. If deposition is also unsubmitted (see <code>submitted</code>) files can be updated as well. </li>
      <li><code>"done"</code>: Deposition has been published.</li></ul>
      <li><code>"error"</code>: Deposition is in an error state - contact our support.</li></ul>
    </td>
</tr>
<tr>
    <td><code>submitted</code></td>
    <td>Bool</td>
    <td>No</td>
    <td>True of deposition has been published, False otherwise.</td>
</tr>
<tr>
    <td><code>title</code></td>
    <td>String</td>
    <td>No</td>
    <td>Title of deposition (automatically set from <code>metadata</code>). Defaults to empty string.</td>
</tr>
</tbody>
</table>
</div>
    </div>
  </div>
  <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-r-meta">
          <h4 id="restapi-rep-meta">Deposition metadata <small></small> <span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-r-meta" class="panel-collapse collapse">
      <div class="panel-body">
<table class="table table-striped">
<thead>
<tr>
  <th class="span2">Attribute</th>
  <th>Type</th>
  <th>Required</th>
  <th>Description</th>
</tr>
</thead>
<tbody>
<tr>
    <td><code>upload_type</code></td>
    <td>String</td>
    <td>Yes</td>
    <td>Controlled vocabulary:<ul>
      <li><code>publication</code>: Publication</li>
      <li><code>poster</code>: Poster</li>
      <li><code>presentation</code>: Presentation</li>
      <li><code>dataset</code>: Dataset</li>
      <li><code>image</code>: Image</li>
      <li><code>video</code>: Video/Audio</li>
      <li><code>software</code>: Software</li>
    </ul></td>
</tr>
<tr>
    <td><code>publication_type</code></td>
    <td>String</td>
    <td>Yes, if <code>upload_type</code> is <code>"publication"</code>.</td>
    <td>Controlled vocabulary:<ul>
      <li><code>book</code>: Book</li>
<li><code>section</code>: Book section</li>
<li><code>conferencepaper</code>: Conference paper</li>
<li><code>article</code>: Journal article</li>
<li><code>patent</code>: Patent</li>
<li><code>preprint</code>: Preprint</li>
<li><code>report</code>: Report</li>
<li><code>softwaredocumentation</code>: Software documentation</li>
<li><code>thesis</code>: Thesis</li>
<li><code>technicalnote</code>: Technical note</li>
<li><code>workingpaper</code>: Working paper</li>
<li><code>other</code>: Other</li>
    </ul></td>
</tr>
<tr>
    <td><code>image_type</code></td>
    <td>String</td>
    <td>Yes, if <code>upload_type</code> is <code>"image"</code>.</td>
    <td>Controlled vocabulary:<ul>
      <li><code>figure</code>: Figure</li>
<li><code>plot</code>: Plot</li>
<li><code>drawing</code>: Drawing</li>
<li><code>diagram</code>: Diagram</li>
<li><code>photo</code>: Photo</li>
<li><code>other</code>: Other</li>
    </ul></td>
</tr>
<tr>
    <td><code>publication_date</code></td>
    <td>String</td>
    <td>Yes</td>
    <td>Date of publication in ISO8601 format (<code>YYYY-MM-DD</code>). Defaults to current date.</td>
</tr>
<tr>
    <td><code>title</code></td>
    <td>String</td>
    <td>Yes</td>
    <td>Title of deposition.</td>
</tr>
<tr>
    <td><code>creators</code></td>
    <td>Array of objects</td>
    <td>Yes</td>
    <td><p>The creators/authors of the deposition. Each array element is an object with the attributes:</p>
    <ul>
      <li><code>name</code>: Name of creator in the format <em>Family name, First names</em></li>
      <li><code>affiliation</code>: Affiliation of creator (optional).</li>
      <li><code>orcid</code>: ORCID identifier of creator (optional).</li>
    </ul>
    <p>Example:</p>
    <pre>[{'name':'Doe, John', 'affiliation': 'Zenodo'},
{'name':'Smith, Jane', 'affiliation': 'Zenodo'}]</pre></td>
</tr>
<tr>
    <td><code>description</code></td>
    <td>String</td>
    <td>Yes</td>
    <td>Abstract or description for deposition. Following HTML tags are allowed: <code>a</code>, <code>p</code>, <code>br</code>, <code>blockquote</code>, <code>strong</code>, <code>b</code>, <code>u</code>, <code>i</code>, <code>em</code>, <code>ul</code>, <code>ol</code>, <code>li</code>, <code>sub</code>, <code>sup</code>, <code>div</code>, <code>strike</code>.</td>
</tr>
<tr>
    <td><code>access_right</code></td>
    <td>String</td>
    <td>Yes</td>
    <td>Controlled vocabulary:<ul>
      <li><code>open</code>: Open Access</li>
<li><code>embargoed</code>: Embargoed Access</li>
<li><code>closed</code>: Closed Access</li>
    </ul>Defaults to <code>open</code>.</td>
</tr>
<tr>
    <td><code>license</code></td>
    <td>String</td>
    <td>Yes, if <code>access_right</code> is <code>"open"</code> or <code>"embargoed"</code>.</td>
    <td><p>Controlled vocabulary based on <a href="http://licenses.opendefinition.org/licenses/groups/all.json">http://licenses.opendefinition.org</a>. The selected license applies to all files in this deposition, but not to the metadata which is licensed under <a href="terms">Creative Commons Zero</a>. Further information about licenses is available at <a href="http://licenses.opendefinition.org/">Open Definition Licenses Service</a>.</p>
    <p>Defaults to <code>cc-by</code> for non-datasets and <code>cc-zero</code> for datasets.</p></td>
</tr>
<tr>
    <td><code>embargo_date</code></td>
    <td></td>
    <td>Yes, if <code>access_right</code> is <code>"embargoed"</code>.</td>
    <td>Date in ISO8601 format (<code>YYYY-MM-DD</code>) when the deposited files will be made automatically made publicly available by the system. Defaults to current date.</td>
</tr>
<tr>
    <td><code>doi</code></td>
    <td>String</td>
    <td>No</td>
    <td>Digital Object Identifier. Did a publisher already assign a DOI to your deposited files? If not, leave the field empty and we will register a new DOI for you when you publish. A DOI allow others to easily and unambiguously cite your deposition.</td>
</tr>
<tr>
    <td><code>prereserve_doi</code></td>
    <td>Object/Bool</td>
    <td>No</td>
    <td>Set to <code>true</code>, to reserve a Digital Object Identifier (DOI). The DOI is automatically generated by our system and cannot be changed. Also, The DOI is not registered with <a href="http://www.datacite.org">DataCite</a> until you publish your deposition, and thus cannot be used before then. Reserving a DOI is useful, if you need to include it in the files you upload, or if you need to provide a dataset DOI to your publisher but not yet publish your dataset. The response from the REST API will include the reserved DOI.</td>
</tr>
<tr>
    <td><code>keywords</code></td>
    <td>Array of strings</td>
    <td>No</td>
    <td><p>Free form keywords for this deposition. Example: </p><code>["Keyword 1", "Keyword 2"]</code></td>
</tr>
<tr>
    <td><code>notes</code></td>
    <td>String</td>
    <td>No</td>
    <td>Additional notes. No HTML allowed.</td>
</tr>
<tr>
    <td><code>related_identifiers</code></td>
    <td>Array of objects</td>
    <td>No</td>
    <td><p>Persistent identifiers of related publications and datasets. Supported identifiers include: DOI, Handle, ARK, PURL, ISSN, ISBN, PubMed ID, PubMed Central ID, ADS Bibliographic Code, arXiv, Life Science Identifiers (LSID), EAN-13, ISTC, URNs and URLs. Each array element is an object with the attributes:</p>
    <ul>
      <li><code>identifier</code>: The persistent identifier</li>
      <li><code>relation</code>: Relationship. Controlled vocabulary (<code>isCitedBy</code>, <code>cites</code>, <code>isSupplementTo</code>, <code>isSupplementedBy</code>, <code>isNewVersionOf</code>, <code>isPreviousVersionOf</code>, <code>isPartOf</code>, <code>hasPart</code>, <code>isIdenticalTo</code>, <code>isAlternateIdentifier</code>).</li>
    </ul>
    <p>Example:</p>
    <pre>[
  {'relation': 'isSupplementTo', 'identifier':'10.1234/foo'},
  {'relation': 'cites', 'identifier':'http://dx.doi.org/10.1234/bar'}
]</pre><p>Note the identifier type (e.g. DOI) is automatically detected, and used to validate and normalize the identifier into a standard form.</p></td>
</tr>
<tr>
    <td><code>references</code></td>
    <td>Array of strings</td>
    <td>No</td>
    <td><p>List of references.</p>
    <p>Example:</p>
    <pre>[
    "Doe J (2014). Title. Publisher. DOI",
    "Smith J (2014). Title. Publisher. DOI"
]</pre>
    </td>
</tr>
<tr>
    <td><code>communities</code></td>
    <td>Array of objects</td>
    <td>No</td>
    <td><p>List of communities you wish the deposition to appear. The owner of the community will be notified, and can either accept or reject your request. Each array element is an object with the attributes:</p>
    <ul>
      <li><code>identifier</code>: Community identifier</li>
    </ul>
    <p>Example:</p>
    <pre>[{'identifier':'ecfunded'}]</pre></td>
</tr>
<tr>
    <td><code>grants</code></td>
    <td>Array of objects</td>
    <td>No</td>
    <td><p>List of European Commission FP7 grants which have funded the research for this deposition. Each array element is an object with the attributes:</p>
    <ul>
      <li><code>id</code>: FP7 grant number.</li>
    </ul>
    <p>Example:</p>
    <pre>[{'id':'283595'}]</pre></td>
</tr>
<tr>
    <td><code>journal_title</code></td>
    <td>String</td>
    <td>No</td>
    <td>Journal title, if deposition is a published article.</td>
</tr>
<tr>
    <td><code>journal_volume</code></td>
    <td>String</td>
    <td>No</td>
    <td>Journal volume, if deposition is a published article.</td>
</tr>
<tr>
    <td><code>journal_issue</code></td>
    <td>String</td>
    <td>No</td>
    <td>Journal issue, if deposition is a published article.</td>
</tr>
<tr>
    <td><code>journal_pages</code></td>
    <td>String</td>
    <td>No</td>
    <td>Journal pages, if deposition is a published article.</td>
</tr>
<tr>
    <td><code>conference_title</code></td>
    <td>String</td>
    <td>No</td>
    <td>Title of conference (e.g. 20th International Conference on Computing in High Energy and Nuclear Physics).</td>
</tr>
<tr>
    <td><code>conference_acronym</code></td>
    <td>String</td>
    <td>No</td>
    <td>Acronym of conference (e.g. CHEP'13).</td>
</tr>
<tr>
    <td><code>conference_dates</code></td>
    <td>String</td>
    <td>No</td>
    <td>Dates of conference (e.g. 14-18 October 2013). Conference title or acronym must also be specified if this field is specified.</td>
</tr>
<tr>
    <td><code>conference_place</code></td>
    <td>String</td>
    <td>No</td>
    <td>Place of conference in the format city, country (e.g. Amsterdam, The Netherlands). Conference title or acronym must also be specified if this field is specified.</td>
</tr>
<tr>
    <td><code>conference_url</code></td>
    <td>String</td>
    <td>No</td>
    <td>URL of conference (e.g. http://www.chep2013.org/).</td>
</tr>
<tr>
    <td><code>conference_session</code></td>
    <td>String</td>
    <td>No</td>
    <td>Number of session within the conference (e.g. VI).</td>
</tr>
<tr>
    <td><code>conference_session_part</code></td>
    <td>String</td>
    <td>No</td>
    <td>Number of part within a session (e.g. 1).</td>
</tr>
<tr>
    <td><code>imprint_publisher</code></td>
    <td>String</td>
    <td>No</td>
    <td>Publisher of a book/report/chapter</td>
</tr>
<tr>
    <td><code>imprint_isbn</code></td>
    <td>String</td>
    <td>No</td>
    <td>ISBN of a book/report</td>
</tr>
<tr>
    <td><code>imprint_place</code></td>
    <td>String</td>
    <td>No</td>
    <td>Place of publication of a book/report/chapter in the format city, country.</td>
</tr>
<tr>
    <td><code>partof_title</code></td>
    <td>String</td>
    <td>No</td>
    <td>Title of book for chapters</td>
</tr>
<tr>
    <td><code>partof_pages</code></td>
    <td>String</td>
    <td>No</td>
    <td>Pages numbers of book</td>
</tr>
<tr>
    <td><code>thesis_supervisors</code></td>
    <td>Array of objects</td>
    <td>No</td>
    <td>Supervisors of the thesis. Same format as for <code>creators</code>.</td>
</tr>
<tr>
    <td><code>thesis_university</code></td>
    <td>String</td>
    <td>No</td>
    <td>Awarding university of thesis.</td>
</tr>
</tbody>
</table>
</div>
    </div>
  </div>
  <div class="panel panel-default">
    <div class="panel-heading info">
        <a class="panel-toggle collapsed" data-toggle="collapse" href="#collapse-r-files">
          <h4 id="restapi-rep-files">Deposition file<small></small> <span class="pull-right show-on-collapsed"><i class="glyphicon glyphicon-chevron-right"></i></span><span class="pull-right hide-on-collapsed"><i class="glyphicon glyphicon-chevron-down"></i></span></h4>
        </a>
    </div>
    <div id="collapse-r-files" class="panel-collapse collapse">
      <div class="panel-body">
<table class="table table-striped">
<thead>
<tr>
  <th class="span2">Attribute</th>
  <th>Type</th>
  <th>Editable</th>
  <th>Description</th>
</tr>
</thead>
<tbody>
<tr>
    <td><code>id</code></td>
    <td>String</td>
    <td>No</td>
    <td>Deposition file identifier</td>
</tr>
<tr>
    <td><code>filename</code></td>
    <td>String</td>
    <td>Yes</td>
    <td>Name of file</td>
</tr>
<tr>
    <td><code>filesize</code></td>
    <td>Integer</td>
    <td>No</td>
    <td>Size of files in bytes</td>
</tr>

<tr>
    <td><code>checksum</code></td>
    <td>String</td>
    <td>No</td>
    <td>MD5 checksum of file, computed by our system. This allows you to check the integrity of the uploaded file.</td>
</tr>
</tbody>
</table>
</div>
    </div>
  </div>
</div>

<!--<h2 id="restapi-faq">FAQ</h2>

<dl>
  <dt>What is the difference between <em>deposition id</em> and <em>record id</em>?</dt>
  <dd></dd>
  <dt>Do you support versioning of files?</dt>
  <dd>No, though we plan to add it in the future.</dd>
  <dt>Can I edit the deposition after it is published?</dt>
  <dd></dd>
  <dt>Can I replace a file after a deposition is published?</dt>
  <dd></dd>
</dl>-->

<h2 id="restapi-changes">Changes</h2>
<dl>
<dt>2014-12-20</dt>
<dd><p>Added new relationship <code>isAlternateIdentifier</code> in subfield <code>relation</code> to <code>related_identifiers</code> in deposition metadata.</p></dd>
<dt>2014-12-10</dt>
<dd><p>Added new relationships <code>hasPart</code>, <code>isPartOf</code> &amp; <code>isIdenticalTo</code> in subfield <code>relation</code> to <code>related_identifiers</code> in deposition metadata.</p></dd>
<dt>2014-11-20</dt>
<dd><p>Added new optional subfield <code>orcid</code> to <code>creators</code> in deposition metadata.</p></dd>
<dt>2014-10-21</dt>
<dd><p>Added new optional fields <code>conference_session</code> and <code>conference_session_part</code> to deposition metadata.</p></dd>
<dt>2014-09-09</dt>
<dd><p>Added new optional field <code>references</code> to deposition metadata.</p></dd>
<dt>2014-06-13</dt>
<dd><p>Authentication changed from API keys to OAuth 2.0. API key authentication is deprecated and will be phased out in October, 2014. Please use <a href="https://zenodo.org/account/settings/applications/">personal access tokens</a> instead of API keys.</p></dd>
<dt>2013-12-18</dt>
<dd><p>REST API version 1.0 final release</p><ul>
<li>Deposition actions moved from <code>deposit/depositions/:id/action</code> to <code>deposit/depositions/:id/actions</code></li>
<li>Added <code>edit</code> and <code>discard</code> deposition action resources.</li>
<li>Deposition resource representation:<ul>
<li><code>state</code>: Controlled vocabulary changed.</li>
<li><code>submitted</code>: Data type changed from Timestamp to Bool.</li></ul></li>
<ul></dd>
<dt>2013-11-13</dt>
<dd><p>REST API initial release candidate</p></dd>
</dl>

<h2 id="harvest"><strong>OAI-PMH API</strong> <small>use OAI-PMH to harvest Zenodo</small></h2>
<hr/>
<p>
Zenodo allows you to harvest our entire repository via
the Open Archives Initiative Protocol for Metadata Harvesting (<a href="http://www.openarchives.org/pmh/">OAI-PMH</a>). OAI-PMH is a widely used protocol for harvesting metadata and most popular repository software provide support for this protocol.
</p>
<p>
All metadata is licensed under <a href="terms">Creative Commons Zero</a>, while the data files may be either open access and subject to a license described in the metadata or closed access and not available for download.
</p>
<h3 id="harvest-baseurl">Base URL</h3>
<p>
<pre align="center">
https://zenodo.org/oai2d
</pre>
</p>

<h3 id="harvest-metadata">Metadata formats</h3>
Metadata for each record is available in several formats. The available formats include:

<dl>
<dt><code>oai_datacite3</code></dt>
<dd><p>OAI DataCite &mdash; This metadata format has been specifically established for the dissemination of DataCite records using OAI-PMH. In addition to the original DataCite v3.0 metadata, this format contains several other elements describing the version of the metadata, whether it is of reference quality, and the registering datacentre. For more information about this format and its schema please see the <a href="http://oai.datacite.org/">DataCite OAI schema</a> web site.</p>
<p><span class="label label-info">Recommended</span> We recommend you harvest using this metadata format. The format contains the most complete metadata and is our primary supported format.</p>
<p><a href="view-source:https://zenodo.org/oai2d?verb=ListRecords&metadataPrefix=oai_datacite3&set=openaire_data">See example</a></p>
</dd>
<dt><code>oai_datacite</code></dt>
<dd><p>OAI DataCite &mdash; This metadata format has been specifically established for the dissemination of DataCite records using OAI-PMH. In addition to the original DataCite metadata, this format contains several other elements describing the version of the metadata, whether it is of reference quality, and the registering datacentre. For more information about this format and its schema please see the <a href="http://oai.datacite.org/">DataCite OAI schema</a> web site.</p>
<p><a href="view-source:https://zenodo.org/oai2d?verb=ListRecords&metadataPrefix=oai_datacite&set=openaire_data">See example</a></p>
</dd>
<dt><code>datacite3</code></dt>
<dd><p>DataCite v3.0 &mdash; This metadata format contains only the original DataCite metadata without additions or alterations. The schema for this format does not exist and metadata will not validate against it. Please note that this format is not OAI-PMH version 2.0 compliant.</p>
<p><a href="view-source:https://zenodo.org/oai2d?verb=ListRecords&metadataPrefix=datacite3&set=openaire_data">See example</a></p>
</dd>
<dt><code>datacite</code></dt>
<dd><p>DataCite v2.2 &mdash; This metadata format contains only the original DataCite metadata without additions or alterations. The schema for this format does not exist and metadata will not validate against it. Please note that this format is not OAI-PMH version 2.0 compliant.</p> <p>
<span class="label">Heads up!</span> We will be upgrading to <a href="http://schema.datacite.org/meta/kernel-3/index.html">DataCite Metadata Schema v3.0</a> and discontinue support for DataCite v2.2, hence please ensure your OAI-PMH client are capable of reading both versions. There are only few backwards incompatible changes between v3.0 and v2.2.
</p>
<p><a href="view-source:https://zenodo.org/oai2d?verb=ListRecords&metadataPrefix=datacite&set=openaire_data">See example</a></p>
</dd>
<dt><code>oai_dc</code></dt>
<dd><p>Dublin Core &mdash; only minimal metadata is included in this format, and is primarily provided for clients which does not support <code>oai_datacite</code>.</p><p><a href="view-source:https://zenodo.org/oai2d?verb=ListRecords&metadataPrefix=oai_dc&set=openaire">See example</a></p></dd>
</dl>

<h3 id="harvest-sets">Sets</h3>
<p>We support both harvesting of the <em>entire repository</em> as well as <em>selective harvesting</em> of communities.</p>
<dl>
<dt><code>zenodo</code></dt>
<dd><p>All of Zenodo</p><p><a href="view-source:https://zenodo.org/oai2d?verb=ListRecords&metadataPrefix=oai_datacite&set=zenodo">See example</a></p></dd>
<dt><code>user-<em>&lt;identifier&gt;</em></code></dt>
<dd><p>Community sets &mdash; allows selective harvesting of specific communities. Replace <code><em>&lt;identifier&gt;</em></code> with the community identifier. Alternatively each community provides a direct harvesting API link on their front-page, which includes the correct community identifier.</p><p><a href="view-source:https://zenodo.org/oai2d?verb=ListRecords&metadataPrefix=oai_datacite&set=user-cfa">See example</a></p></dd>
</dl>
<p>If you need selective harvesting and your use case is not supported by above sets, please <a href="contact">contact us</a> and we may possible set a specific set for you.</p>

<h3 id="harvest-schedule">Update schedule</h3>
Sets are updated once an hour.

<h3 id="harvest-ratelimit">Rate limit</h3>
The OAI-PMH API is rated limited to one request per 2 seconds. We would be grateful if you <a href="/contact">notify us</a> that you are harvesting us and in which context. It allows us to take your use case into consideration for future developments.

<h3 id="harvest-changes">Changes</h3>
<dl>
<dt>2014-03-10</dt>
<dd><p>Added metadata formats <code>datacite3</code> and <code>oai_datacite3</code> to support DataCite v3.0.</p></dd>
<dt>2013-05-08</dt>
<dd><p>Initial release of OAI-PMH API</p></dd>
</dl>

<!--
<h2 id="metadata"><strong>Metadata API</strong> <small>machine readable formats of records</small></h2>
<hr/>
<p>Metadata for individual records are exportable in several different machine readable formats. All metadata is licensed under <a href="terms">Creative Commons Zero</a>, while the data files may be either open access and subject to a license described in the metadata or closed access and not available for download.
</p>

<h3 id="metadata-url">URL pattern</h3>
<pre align="center">
https://zenodo.org/record/<em>&lt;record id&gt;</em>/export/<em>&lt;format id&gt;</em>
</pre>
<p>Please replace <code>&lt;record id&gt;</code> with the record id of interest (e.g. obtained from the REST API), and replace <code>&lt;format id&gt;</code> with one of the metadata formats listed below.</p>

<h3 id="metadata-metadata">Metadata formats</h3>
The following metadata formats are supported:

<dl>
<dt><code>dcite</code></dt>
<dd><p>DataCite Metadata v2.2. The format contains the most complete metadata and is our primary supported format.</p> <p>
<span class="label label-info">Heads up!</span> We will be upgrading to <a href="http://schema.datacite.org/meta/kernel-3/index.html">DataCite Metadata Schema v3.0</a> and discontinue support for DataCite v2.2, hence please ensure you can parse both versions. There are only few backwards incompatible changes between v3.0 and v2.2.
</p>
<p><a href="">See example</a></p>
</dd>
<dt><code>dc</code></dt>
<dd><p>Dublin Core &mdash; only minimal metadata is included in this format, and is primarily provided for clients which does not support <code>dcite</code>.</p><p><a href="">See example</a></p></dd>
<dt><code>xm</code></dt>
<dd><p>MARC XML  &mdash;</p>
<p><a href="">See example</a></p></dd>
</dl>

<h3 id="metadata-changes">Changes</h3>
<dt>2013-05-08</dt>
<dd><p>Initial release of Metadata API</p></dd>
</dl>
-->
</div>
</div>

"""
