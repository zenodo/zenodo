include ../../config.mk
-include ../../config-local.mk

FLASHFILES = *.swf

FLASHDIR = $(WEBDIR)/flash/

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -d $(FLASHDIR)
	$(INSTALL) -m 664 $(FLASHFILES) $(FLASHDIR)

clean:
	@rm -f *.orig *~
	@echo "Done."
