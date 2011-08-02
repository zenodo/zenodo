include ../../config.mk
-include ../../config-local.mk

CSSFILES = *.css
PNGFILES = *.png

CSSDIR = $(WEBDIR)/css/
PNGDIR = $(WEBDIR)/css/images/

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -d $(CSSDIR)
	$(INSTALL) -d $(PNGDIR)
	$(INSTALL) -m 664 $(CSSFILES) $(CSSDIR)
	$(INSTALL) -m 664 $(PNGFILES) $(PNGDIR)

clean:
	@rm -f *.orig *~
	@echo "Done."
