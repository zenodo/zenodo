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
# Note that local makefile configurations can be defined in config-local.mk to override config.mk.
#
# For instance for installing on Ubuntu:
#   INSTALL = install -g www-data -m 775
# 
# or for installing in a virtualenv:
#   INSTALL = install -m 775
#   PREFIX = /path/to/venv/
#   PYTHON = /path/to/venv/bin/python

include config.mk
-include config-local.mk

SUBDIRS = bibformat bibsched miscutil openaire websession webstyle

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done.  Please run make test now."

test:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make test && cd .. ;)
	@echo "Done.  Please run make install now."

install:
	@echo "Installing new code and support files..."
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
	@echo "Done.  You may want to copy $(ETCDIR)/invenio-local.conf-example to $(ETCDIR)/invenio-local.conf, edit commented parts, run inveniocfg --update-all --reset-all and restart Apache now."
	@echo "To install database changes, run 'make install-dbchanges'."

install-tables:
	$(BINDIR)/dbexec < openaire/sql/tabcreate.sql

clean:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make clean && cd .. ;)
	@rm -f *.orig *~
	@echo "Done."