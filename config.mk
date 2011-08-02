# Override these settings for the Makefiles in a separate file named:
#     config-local.mk
# in your top level directory
#

PREFIX = /opt/invenio

BINDIR = $(PREFIX)/bin
ETCDIR = $(PREFIX)/etc
TMPDIR = $(PREFIX)/tmp
LIBDIR = $(PREFIX)/lib
WEBDIR = $(PREFIX)/var/www

INSTALL = install -g apache -m 775

PYTHON = /usr/bin/python
