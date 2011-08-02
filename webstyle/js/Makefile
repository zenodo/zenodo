include ../../config.mk
-include ../../config-local.mk

JSFILES = *.js

JSDIR = $(WEBDIR)/js/

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(JSFILES) $(JSDIR)

clean:
	@rm -f *.orig *~
	@echo "Done."
