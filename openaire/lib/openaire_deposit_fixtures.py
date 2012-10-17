# -*- encoding: utf8 -*-
#
## This file is part of Invenio.
## Copyright (C) 2010, 2011, 2012 CERN.
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

"""
Module used in testing of the deposit engine.
"""

FIXTURES = {
    'publishedArticle': {
        'access_rights': 'embargoedAccess',
        'embargo_date': '2012-12-24',
        'authors': 'Kjell, Utne: Institute of Marine Research, Bergen, Norway\nGeir, Huse: Institute of Marine Research, Bergen, Norway\nGeir, Ottersen: Institute of Marine Research, Oslo, Norway\nVladimir, Zabavnikov: Remote Sensing Laboratory, Knipovich Polar Research Institute of Marine Fisheries and Oceanography (PINRO), Murmansk, Russia\nJane Arge, Jacobsen: Faroe Marine Research Institute, Tórshavn, Faroe Islands\nÓskarsson, Guđmundur: Marine Research Institute, Reykjavik, Iceland\nNøttestad, Leif: Institute of Marine Research, Bergen, Norway',
        'title': 'Horizontal distribution and overlap of planktivorous fish stocks in the Norwegian Sea during summers 1995–2006',
        'abstract': 'The Norwegian Sea harbours several large pelagic fish stocks, which use the area for feeding during the summer. The period 1995–2006 had some of the highest biomass of pelagic fish feeding in the Norwegian Sea on record. Here we address the horizontal distribution and overlap between herring, blue whiting and mackerel in this period during the summers using a combination of acoustic, trawl and LIDAR data. A newly developed temperature atlas for the Norwegian Sea is used to present the horizontal fish distributions in relation to temperature. The centre of gravity of the herring distribution changed markedly several times during the investigated period. Blue whiting feeding habitat expanded in a northwestern direction until 2003, corresponding with an increase in abundance. Strong year classes of mackerel in 2001 and 2002 and increasing temperatures throughout the period resulted in an increased amount of mackerel in the Norwegian Sea. Mackerel was generally found in waters warmer than 8°C, while herring and blue whiting were mainly found in water masses between 2 and 8°C. The horizontal overlap between herring and mackerel was low, while blue whiting had a large horizontal overlap with both herring and mackerel. The changes in horizontal distribution and overlap between the species are explained by increasing stock sizes, increasing water temperature and spatially changing zooplankton densities in the Norwegian Sea.',
        'language': 'eng',
        'original_title': '',
        'original_abstract': '',
        'publication_type': 'publishedArticle',
        'projects': '283595',
        'publication_date': '2012-04-25',
        'journal_title': 'Marine Biology Research',
        'doi': '10.1080/17451000.2011.640937',
        'volume': '8',
        'issue': '5-6',
        'pages': '420-441',
        'keywords': 'Herring\nblue whiting\ncompetition\ninteraction\nmackerel\ntemperature',  # Alphabetic order (otherwise assert will fail)
        'notes': 'Test notes',
        'report_pages_no': '6',
        'related_publications': '10.1234/pub\ndoi:10.1234/pub2',
        'related_datasets': '10.1000/data\n10.1000/data2',
    },
    'report': {
        'access_rights': 'openAccess',
        'embargo_date': '',
        'authors': 'Bégin, Marc Elian: SIXSQ SARL',
        'title': 'Release of StratusLab 2.0 Beta',
        'abstract': 'StratusLab uses agile software development methodologies, specifically Scrum, to produce public beta releases every six to eight weeks. Each release builds on the previous ones to provide additional features or more robust implementations of services. This document describes the latest 2.0 beta release, called v1.4, as stepping stone towards the final 2.0 production release in May 2012.',
        'language': 'eng',
        'original_title': '',
        'original_abstract': '',
        'publication_type': 'report',
        'projects': '261552',
        'publication_date': '2012-05-02',
        'journal_title': 'Marine Biology Research',
        'doi': '',
        'volume': '8',
        'issue': '5-6',
        'pages': '420-441',
        'keywords': 'Keyword 1\nKeyword 2',
        'notes': 'Test notes',
        'report_pages_no': '6',
        'isbn': '0-06-251587-X',
        'related_publications': '10.1234/pub\ndoi:10.1234/pub2',
        'related_datasets': '10.1000/data\n10.1000/data2',
        'report_type': 'other',
        'publisher' : 'CERN',
        'place' : 'Geneva',
        'extra_report_numbers' : 'OPENAIRE-VIGGO',
    },
    'data': {
        'accept_cc0_license': 'yes',    
        'access_rights': 'embargoedAccess',
        'embargo_date': '', # Set to empty on purpose (to check if access_rights is considered for data 
        'authors': 'Nielsen, Lars Holm: CERN',
        'title': 'Anonymised Invenio Usage Logs',
        'abstract': 'This is some brand new data.',
        'language': 'eng',  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! (for orginal title?)
        'original_title': '',
        'original_abstract': '',
        'publication_type': 'data',
        'projects': '261552',
        'publication_date': '2012-05-02',
        'journal_title': 'Marine Biology Research',
        'doi': '',
        'volume': '8',
        'issue': '5-6',
        'pages': '420-441',
        'keywords': 'Keyword 1\nKeyword 2',
        'notes': 'Test notes',
        'report_pages_no': '6',
        'related_publications': '10.1234/pub\ndoi:10.1234/pub2',
        'related_datasets': '10.1000/data\n10.1000/data2',
        'dataset_publisher': 'Dryad Digital Repository',
    },
}

MARC_FIXTURES = {}
MARC_FIXTURES['publishedArticle'] = """
0247  $$a10.1080/17451000.2011.640937$$2DOI
RE:037   \$\$aOpenAIRE-OPENAIREPLUS-2012-[0-9]+$
041   $$aeng
100   $$aKjell, Utne$$uInstitute of Marine Research, Bergen, Norway
245   $$aHorizontal distribution and overlap of planktivorous fish stocks in the Norwegian Sea during summers 1995–2006
260   $$c2012-04-25
500   $$aTest notes
520   $$aThe Norwegian Sea harbours several large pelagic fish stocks, which use the area for feeding during the summer. The period 1995–2006 had some of the highest biomass of pelagic fish feeding in the Norwegian Sea on record. Here we address the horizontal distribution and overlap between herring, blue whiting and mackerel in this period during the summers using a combination of acoustic, trawl and LIDAR data. A newly developed temperature atlas for the Norwegian Sea is used to present the horizontal fish distributions in relation to temperature. The centre of gravity of the herring distribution changed markedly several times during the investigated period. Blue whiting feeding habitat expanded in a northwestern direction until 2003, corresponding with an increase in abundance. Strong year classes of mackerel in 2001 and 2002 and increasing temperatures throughout the period resulted in an increased amount of mackerel in the Norwegian Sea. Mackerel was generally found in waters warmer than 8°C, while herring and blue whiting were mainly found in water masses between 2 and 8°C. The horizontal overlap between herring and mackerel was low, while blue whiting had a large horizontal overlap with both herring and mackerel. The changes in horizontal distribution and overlap between the species are explained by increasing stock sizes, increasing water temperature and spatially changing zooplankton densities in the Norwegian Sea.
536   $$aOPENAIREPLUS - 2nd-Generation Open Access Infrastructure for Research in Europe (283595)$$c283595
542   $$lembargoedAccess
6531  $$aHerring
6531  $$ablue whiting
6531  $$acompetition
6531  $$ainteraction
6531  $$amackerel
6531  $$atemperature
700   $$aGeir, Huse$$uInstitute of Marine Research, Bergen, Norway
700   $$aGeir, Ottersen$$uInstitute of Marine Research, Oslo, Norway
700   $$aVladimir, Zabavnikov$$uRemote Sensing Laboratory, Knipovich Polar Research Institute of Marine Fisheries and Oceanography (PINRO), Murmansk, Russia
700   $$aJane Arge, Jacobsen$$uFaroe Marine Research Institute, Tórshavn, Faroe Islands
700   $$aÓskarsson, Guđmundur$$uMarine Research Institute, Reykjavik, Iceland
700   $$aNøttestad, Leif$$uInstitute of Marine Research, Bergen, Norway
773   $$a10.1000/data$$ndata
773   $$a10.1000/data2$$ndata
8560  $$flars.holm.nielsen@cern.ch$$yLars Holm Nielsen
909C4 $$pMarine Biology Research$$y2012$$n5-6$$v8$$c420-441
942   $$a2012-12-24
980   $$aPROVISIONAL
980   $$aOPENAIRE
"""

MARC_FIXTURES['report'] = """
020   $$a0-06-251587-X
RE:037   \$\$aOpenAIRE-OPENAIREPLUS-2012-[0-9]+$
041   $$aeng
088   $$aOPENAIRE-VIGGO
100   $$aBégin, Marc Elian$$uSIXSQ SARL
245   $$aRelease of StratusLab 2.0 Beta
260   $$c2012-05-02
260   $$aGeneva$$bCERN$$c2012
300   $$a6
500   $$aTest notes
520   $$aStratusLab uses agile software development methodologies, specifically Scrum, to produce public beta releases every six to eight weeks. Each release builds on the previous ones to provide additional features or more robust implementations of services. This document describes the latest 2.0 beta release, called v1.4, as stepping stone towards the final 2.0 production release in May 2012.
536   $$aOPENAIREPLUS - 2nd-Generation Open Access Infrastructure for Research in Europe (283595)$$c283595
542   $$lopenAccess
6531  $$aKeyword 1
6531  $$aKeyword 2
773   $$a10.1000/data$$ndata
773   $$a10.1000/data2$$ndata
8560  $$flars.holm.nielsen@cern.ch$$yLars Holm Nielsen
980   $$aPROVISIONAL
980   $$bREPORT_OTHER
980   $$aREPORTS
"""

MARC_FIXTURES['data'] = """
RE:037   \$\$aOpenAIRE-OPENAIREPLUS-2012-[0-9]+$
041   $$aeng
100   $$aNielsen, Lars Holm$$uCERN
245   $$aAnonymised Invenio Usage Logs
260   $$c2012-05-02
260   $$bDryad Digital Repository$$c2012
500   $$aTest notes
520   $$aThis is some brand new data.
536   $$aOPENAIREPLUS - 2nd-Generation Open Access Infrastructure for Research in Europe (283595)$$c283595
542   $$lcc0
6531  $$aKeyword 1
6531  $$aKeyword 2
773   $$a10.1234/pub$$npub
773   $$a10.1234/pub2$$npub
8560  $$flars.holm.nielsen@cern.ch$$yLars Holm Nielsen
980   $$aPROVISIONAL
980   $$aDATA
"""
