include config.mk
-include config-local.mk
#
# Note that local makefile configurations can be defined in config-local.mk to override config.mk

SUBDIRS = bibformat bibsched miscutil openaire websession webstyle

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done.  Please run make test now."

test:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make test && cd .. ;)
	@echo "Done.  Please run make install now."

install:
	@echo "Installing new code and support files..."
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
	@echo "Done.  You may want to copy $(ETCDIR)/invenio-local.conf-example to $(ETCDIR)/invenio-local.conf, edit commented parts, run inveniocfg --update-all --reset-all and restart Apache now."
	@echo "To install database changes, run 'make install-dbchanges'."

clean:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make clean && cd .. ;)
	@rm -f *.orig *~
	@echo "Done."

