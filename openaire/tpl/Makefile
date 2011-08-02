include ../../config.mk
-include ../../config-local.mk

TPLFILES = *.tpl

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -d $(ETCDIR)
	$(INSTALL) -m 664 $(TPLFILES) $(ETCDIR)

clean:
	@rm -f *.orig *~
	@echo "Done."
