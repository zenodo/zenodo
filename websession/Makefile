include ../config.mk
-include ../config-local.mk

LIBFILES = *.py

LIBDIR = $(PREFIX)/lib/python/invenio/

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(LIBFILES) $(LIBDIR)

clean:
	@rm -f *.orig *~
	@echo "Done."
