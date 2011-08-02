include ../config.mk
-include ../config-local.mk

BSTFILES = *.py

BSTDIR = $(PREFIX)/lib/python/invenio/bibsched_tasklets/

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -d $(BSTDIR)
	$(INSTALL) -m 664 $(BSTFILES) $(BSTDIR)

clean:
	@rm -f *.orig *~
	@echo "Done."
