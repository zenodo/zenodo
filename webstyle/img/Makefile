include ../../config.mk
-include ../../config-local.mk

IMGFILES = *.png *.jpeg

IMGDIR = $(WEBDIR)/img/

all:
	@echo "Done."

test:
	@echo "Nothing to test."

install:
	$(INSTALL) -d $(IMGDIR)
	$(INSTALL) -m 664 $(IMGFILES) $(IMGDIR)

clean:
	@rm -f *.orig *~
	@echo "Done."
