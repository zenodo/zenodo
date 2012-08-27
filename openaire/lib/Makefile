include ../../config.mk
-include ../../config-local.mk

LIBFILES = *.py
MIGRATIONFILES = migrations/*.py

LIBDIR = $(PREFIX)/lib/python/invenio/
MIGRATIONDIR = $(PREFIX)/lib/python/invenio/migrations/

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -d $(LIBDIR)
	$(INSTALL) -d $(MIGRATIONDIR)
	$(INSTALL) -m 664 $(LIBFILES) $(LIBDIR)
	$(INSTALL) -m 664 $(MIGRATIONFILES) $(MIGRATIONDIR)

clean:
	@rm -f *.orig *~
	@echo "Done."
