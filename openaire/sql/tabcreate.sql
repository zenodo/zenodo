-- This file is part of Invenio.
-- Copyright (C) 2010, 2011 CERN.
--
-- Invenio is free software; you can redistribute it and/or
-- modify it under the terms of the GNU General Public License as
-- published by the Free Software Foundation; either version 2 of the
-- License, or (at your option) any later version.
--
-- Invenio is distributed in the hope that it will be useful, but
-- WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
-- General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Invenio; if not, write to the Free Software Foundation, Inc.,
-- 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

-- OpenAIRE specific tables
CREATE TABLE IF NOT EXISTS OpenAIREauthorships (
  uid int(15) NOT NULL,
  publicationid varchar(30) NOT NULL,
  authorship varchar(255) NOT NULL,
  UNIQUE (uid, publicationid, authorship),
  KEY (uid, publicationid),
  KEY (uid, authorship),
  KEY (authorship)
) ENGINE=MyISAM;

CREATE TABLE IF NOT EXISTS OpenAIREkeywords (
  uid int(15) NOT NULL,
  publicationid varchar(30) NOT NULL,
  keyword varchar(255) NOT NULL,
  KEY (uid, publicationid),
  KEY (uid, keyword),
  KEY (keyword)
) ENGINE=MyISAM;


CREATE TABLE IF NOT EXISTS eupublication (
  publicationid varchar(255) NOT NULL,
  projectid int(15) NOT NULL,
  uid int(15) NOT NULL,
  id_bibrec int(15) NULL default NULL,
  UNIQUE KEY (publicationid, projectid, uid),
  KEY (publicationid),
  KEY (projectid),
  KEY (uid),
  KEY (id_bibrec)
) ENGINE=MyISAM;

CREATE TABLE IF NOT EXISTS pgreplayqueue (
  id int(15) unsigned NOT NULL auto_increment,
  query longblob,
  first_try datetime NOT NULL default '0000-00-00',
  last_try datetime NOT NULL default '0000-00-00',
  PRIMARY KEY (id)
) ENGINE=MyISAM;

CREATE TABLE IF NOT EXISTS dbmigrations (
  id int(15) unsigned NOT NULL auto_increment,
  module varchar(255) NOT NULL,
  migration varchar(255) NOT NULL,
  applied DATETIME NOT NULL,
  PRIMARY KEY (id),
  KEY (migration)
) ENGINE=MyISAM;

-- end of file
