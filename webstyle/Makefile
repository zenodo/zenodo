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

include ../config.mk
-include ../config-local.mk

all: sdist
	@echo "Done."

sdist:
	$(PYTHON) setup.py $(SDIST_ARGS)

test:
	@echo "Nothing to test."

develop:
	$(PIP_DEVELOP) .

install:
	$(PIP_INSTALL) dist/*.tar.gz

uninstall:
	$(PIP_UNINSTALL) openaire-webstyle

clean:
	@rm -Rf dist/ *.egg-info/ build/
	@echo "Done."