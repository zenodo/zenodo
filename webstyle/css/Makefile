include ../../config.mk
-include ../../config-local.mk

CSSFILES = *.css

CSSDIR = $(WEBDIR)/css/

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -m 664 $(CSSFILES) $(CSSDIR)

clean:
	@rm -f *.orig *~
	@echo "Done."
