include ../../config.mk
-include ../../config-local.mk

LIBFILES = *.py
JSFILES = *.js

LIBDIR = $(PREFIX)/lib/python/invenio/
JSDIR = $(PREFIX)/var/www/js/

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -d $(LIBDIR)
	$(INSTALL) -d $(JSDIR)
	$(INSTALL) -m 664 $(LIBFILES) $(LIBDIR)
	$(INSTALL) -m 664 $(JSFILES) $(JSDIR)

clean:
	@rm -f *.orig *~
	@echo "Done."
