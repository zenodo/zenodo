include ../../config.mk
-include ../../config-local.mk

JSFILES = *.js

JSDIR = $(PREFIX)/var/www/js/

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -d $(JSDIR)
	$(INSTALL) -m 664 $(JSFILES) $(JSDIR)

clean:
	@rm -f *.orig *~
	@echo "Done."