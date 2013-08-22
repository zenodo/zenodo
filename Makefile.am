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
#
#

confignicedir = $(sysconfdir)/build
confignice_SCRIPTS=config.nice

SUBDIRS = bibfield bibedit bibformat bibsched miscutil openaire websearch websession webstyle

EXTRA_DIST = config.nice.in config.rpath

install-tables:
	${prefix}/bin/dbexec < $(top_srcdir)/openaire/sql/tabcreate.sql

CLEANFILES = *~ *.pyc *.tmp