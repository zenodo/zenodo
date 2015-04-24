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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""AFS volume usage metrics."""

from __future__ import absolute_import

import os
import os.path
import re

from invenio.base.globals import cfg
from invenio.utils.shell import run_shell_command

from ..models import Metric


class AFSVolumeMetric(Metric):

    """Compute AFS volume usage metrics."""

    PATTERN = re.compile("([a-z0-9\.]+)\s+(\d+)\s+(\d+)\s+(\d+)%\s+(\d+)%")

    metric_class = "afs"
    object_type = "AFS Volume"

    @classmethod
    def _parse_output(cls, output):
        s = cls.PATTERN.match(output.splitlines()[-1])
        if s:
            return dict(
                volume=s.group(1),
                quota=s.group(2),
                used=s.group(3),
                used_percent=s.group(4),
            )
        return None

    @classmethod
    def _list_quota(cls, directory):
        if not os.path.isdir(directory):
            return None

        (ret, output, err) = run_shell_command(
            "fs listquota {}".format(directory))

        if ret == 0:
            return cls._parse_output(output)
        return None

    @classmethod
    def all(cls):
        """Compute used space per user."""
        data = dict()

        for d in cfg.get("QUOTAS_AFSMETRIC_DIRECTORIES", []):
            for subdir in os.listdir(os.path.join(cfg['CFG_PREFIX'], d)):
                quota = cls._list_quota(os.path.join(
                    cfg['CFG_PREFIX'], d, subdir))
                if quota:
                    data[quota['volume']] = dict(usage=quota['used_percent'])

        return data.items()
