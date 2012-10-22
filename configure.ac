## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

## This is OpenAIRE main configure.ac file.  If you change this
## file, then please run "autoreconf" to regenerate the "configure"
## script.

## Initialize autoconf and automake:
AC_INIT([openaire],
        m4_esyscmd([./git-version-gen]),
        [openaire-support@cern.ch])
AM_INIT_AUTOMAKE([tar-ustar])

## By default we shall install into /opt/invenio.  (Do not use
## AC_PREFIX_DEFAULT for this, because it would not work well with
## the localstatedir hack below.)
test "${prefix}" = NONE && prefix=/opt/invenio

## Remove eventual trailing slashes from the prefix value:
test "${prefix%/}" != "" && prefix=${prefix%/}

## Check for install:
AC_PROG_INSTALL

## Check for gettext support:
AM_GNU_GETTEXT(external)
AM_GNU_GETTEXT_VERSION(0.14.4)

## Check for MySQL client:
AC_MSG_CHECKING(for mysql)
AC_ARG_WITH(mysql, AC_HELP_STRING([--with-mysql], [path to a specific MySQL binary (optional)]), MYSQL=${withval})
if test -n "$MYSQL"; then
   AC_MSG_RESULT($MYSQL)
else
   AC_PATH_PROG(MYSQL, mysql)
   if test -z "$MYSQL"; then
      AC_MSG_ERROR([
      MySQL command-line client was not found in your PATH.
      Please install it first.
      Available from <http://mysql.com/>.])
   fi
fi

## Check for Python:
AC_MSG_CHECKING(for python)
AC_ARG_WITH(python, AC_HELP_STRING([--with-python], [path to a specific Python binary (optional)]), PYTHON=${withval})
if test -n "$PYTHON"; then
   AC_MSG_RESULT($PYTHON)
else
   AC_PATH_PROG(PYTHON, python)
   if test -z "$PYTHON"; then
      AC_MSG_ERROR([
      Python was not found in your PATH.  Please either install it
      in your PATH or specify --with-python configure option.
      Python is available from <http://python.org/>.])
   fi
fi

### Check for Python version and modules:
#AC_MSG_CHECKING(for required Python modules)
#$PYTHON ${srcdir}/configure-tests.py
#if test $? -ne 0; then
#   AC_MSG_ERROR([Please fix the above Python problem before continuing.])
#fi
#AC_MSG_RESULT(found)

## Substitute variables:
AC_SUBST(VERSION)
AC_SUBST(MYSQL)
AC_SUBST(PYTHON)
AC_SUBST(localstatedir, `eval echo "${localstatedir}"`)

## Define output files:
AC_CONFIG_FILES([config.nice  \
     Makefile \
     bibformat/Makefile \
     bibformat/lib/Makefile \
     bibformat/lib/bibformat_elements/Makefile \
     bibformat/output_formats/Makefile \
     bibformat/format_templates/Makefile \
     bibsched/Makefile \
     bibsched/lib/Makefile \
     bibsched/lib/bibsched_tasklets/Makefile \
     miscutil/Makefile \
     miscutil/lib/Makefile \
     openaire/js/Makefile \
     openaire/sql/Makefile \
     openaire/Makefile \
     openaire/lib/Makefile \
     openaire/tpl/Makefile \
     openaire/upgrades/Makefile \
     websession/Makefile \
     websession/lib/Makefile \
     webstyle/js/Makefile \
     webstyle/css/Makefile \
     webstyle/Makefile \
     webstyle/lib/Makefile \
     webstyle/img/Makefile \
     webstyle/flash/Makefile \
     ])

## Finally, write output files:
AC_OUTPUT

## Write help:
AC_MSG_RESULT([****************************************************************************])
AC_MSG_RESULT([** Your OpenAIRE installation is now ready for building.                  **])
AC_MSG_RESULT([** You have entered the following parameters:                             **])
AC_MSG_RESULT([**   - OpenAIRE main install directory: ${prefix}])
AC_MSG_RESULT([**   - Python executable: $PYTHON])
AC_MSG_RESULT([**   - MySQL client executable: $MYSQL])
AC_MSG_RESULT([** Here are the steps to continue the building process:                   **])
AC_MSG_RESULT([**   1) Type 'make' to build your OpenAIRE system.                        **])
AC_MSG_RESULT([**   2) Type 'make install' to install your OpenAIRE system.              **])
AC_MSG_RESULT([**   2) Type 'make install-tables' to create database tables.             **])
AC_MSG_RESULT([** Afterwards you might want to run:                                      **])
AC_MSG_RESULT([**   1) inveniocfg --update-all                                           **])
AC_MSG_RESULT([**   2) inveniocfg --migrate                                              **])
AC_MSG_RESULT([****************************************************************************])

## end of file
