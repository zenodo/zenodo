include ../../config.mk
-include ../../config-local.mk

LIBFILES = *.py
MIGRATIONFILES = migrations/*.py
JSFILES = *.js

LIBDIR = $(PREFIX)/lib/python/invenio/
MIGRATIONDIR = $(PREFIX)/lib/python/invenio/migrations/
JSDIR = $(PREFIX)/var/www/js/

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -d $(LIBDIR)
	$(INSTALL) -d $(MIGRATIONDIR)
	$(INSTALL) -d $(JSDIR)
	$(INSTALL) -m 664 $(LIBFILES) $(LIBDIR)
	$(INSTALL) -m 664 $(MIGRATIONFILES) $(MIGRATIONDIR)
	$(INSTALL) -m 664 $(JSFILES) $(JSDIR)

clean:
	@rm -f *.orig *~
	@echo "Done."
