# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
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


import numpy as np
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


def create_badge(text, output_path, font_path, template_path):
    """
    Create a DOI badge
    """
    font = ImageFont.truetype(font_path, 11)

    # Open template
    arr = np.asarray(Image.open(template_path))

    # Get left vertical strip for the DOI label
    label_strip = arr[:, 2]
    value_strip = arr[:, 3]

    # Splice into array
    label_width = 28
    value_width = 6 + font.getsize(text)[0]

    for i in xrange(label_width):
        arr = np.insert(arr, 3, label_strip, 1)
    for i in xrange(value_width):
        arr = np.insert(arr, label_width + 4, value_strip, 1)

    im = Image.fromarray(arr)
    draw = ImageDraw.Draw(im)
    draw.text(
        (6, 4),
        "DOI",
        (255, 255, 255),
        font=font
    )
    draw.text(
        (label_width + 8, 4),
        text,
        (255, 255, 255),
        font=font
    )
    im.save(output_path)
