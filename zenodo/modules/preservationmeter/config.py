# -*- coding: utf-8 -*-
#
# This file is part of ZENODO.
# Copyright (C) 2014 CERN.
#
# ZENODO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ZENODO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

PRESERVATIONMETER_FILES_FIELD = '_files'
"""Record key for retrieve files."""

PRESERVATIONMETER_FILES_QUALITY = {
    # Publications
    '.pdf': 100,
    '.htm': 100,
    '.html': 100,
    '.txt': 100,
    '.odt': 95,
    '.rtf': 90,
    '.docx': 60,
    '.doc': 40,

    # Datasets
    '.xml': 100,
    '.csv': 100,
    '.xlsx': 60,
    '.xls': 40,
    '.por': 100,
    '.tab': 100,
    '.tfw': 100,
    '.dwg': 100,
    '.shp': 100,
    '.shx': 100,
    '.dbf': 100,
    '.sav': 50,
    '.dta': 50,
    '.mdb': 50,
    '.accdb': 50,
    '.dbf': 50,
    '.ods': 50,
    '.mif': 50,
    '.kml': 50,
    '.ai': 50,
    '.dxf': 50,
    '.svg': 50,

    # Images & Posters
    '.tif': 100,
    '.jpeg': 90,
    '.jpg': 90,
    '.tiff': 80,
    '.raw': 70,
    '.psd': 50,

    # Presentations

    # Videos
    '.flac': 100,
    '.mp4': 100,
    '.mj2': 100,
    '.mp3': 75,
    '.aif': 75,
    '.wav': 75,

    # Compressed, relevant?
    '.zip': 100,
    '.tar': 90,
    '.gz': 100,
    '.7z': 100,
    '.rar': 70
}
