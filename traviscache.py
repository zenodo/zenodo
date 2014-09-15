# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2014 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.


import argparse
import boto
import hashlib
import os
import subprocess
from boto.s3.key import Key
from boto.exception import S3ResponseError
from boto.s3.connection import Location


def get_parser():
    parser = argparse.ArgumentParser(description='Travis CI Build Cache.')
    parser.add_argument('command', metavar='CMD', help='get, build or set',
                        )
    parser.add_argument('files', metavar='FILE', nargs='+',
                        help='files/directories to cache')
    parser.add_argument('-c', dest='checksum_file', metavar='FILE',
                        action='store', type=file,
                        help='compute checksum from file',
                        required=True)
    parser.add_argument('-b', dest='bucket', action='store',
                        help='Amazon S3 bucket', required=True)
    parser.add_argument('-u', dest='accesskey', action='store',
                        help='Amazon S3 Access Key')
    parser.add_argument('-p', dest='secretkey', action='store',
                        help='Amazon S3 Secret Key')
    parser.add_argument('-f', dest='folder', action='store',
                        help='Amazon S3 Bucket folder', required=True)
    parser.add_argument('-n', dest='name', action='store',
                        help='Cache name (part of filename)', required=True)
    return parser


#
# Amazon S3 methods
#
def _s3_bucket(args):
    return boto.connect_s3(args.accesskey, args.secretkey).get_bucket(
        args.bucket
    )


def _s3_set(args, keyname, filename):
    try:
        bucket = _s3_bucket(args)
    except S3ResponseError:
        bucket = boto.connect_s3(args.accesskey, args.secretkey).create_bucket(
            args.bucket,
            location=Location.DEFAULT
        )
    k = Key(bucket)
    k.key = keyname
    k.set_contents_from_filename(filename)


def _s3_get(args, keyname, filename):
    try:
        k = _s3_bucket(args).get_key(keyname)
        k.get_contents_to_filename(filename)
        return True
    except (S3ResponseError, AttributeError):
        return False


#
# Utils commands
#
def _make_keyname(args, basename):
    return "{0}/{1}.tar.gz".format(args.folder, basename)


def _make_basename(args):
    return "{0}-{1}".format(args.name, _checksum(args))


def _make_filename(basename):
    return basename + ".tar.gz"


def _checksum(args):
    m = hashlib.sha256()
    buf = args.checksum_file.read(65536)
    while len(buf) > 0:
        m.update(buf)
        buf = args.checksum_file.read(65536)
    return m.hexdigest()


def _create_cache(args, filename):
    cmd = ["tar", "-cvf", filename] + args.files
    subprocess.call(cmd)


def _extract_cache(filename):
    cmd = ["tar", "-xvf", filename, '-C', '/']
    subprocess.call(cmd)


#
# Script commands
#
def cache_get(args):
    basename = _make_basename(args)
    keyname = _make_keyname(args, basename)
    filename = _make_filename(basename)
    if _s3_get(args, keyname, filename):
        _extract_cache(filename)


def cache_set(args):
    basename = _make_basename(args)
    keyname = _make_keyname(args, basename)
    filename = _make_filename(basename)

    # Only create an upload archive it if the archive already doesn't exists.
    if not os.path.exists(filename):
        _create_cache(args, filename)
        _s3_set(args, keyname, filename)


#
# Main
#
def main():
    args = get_parser().parse_args()

    if args.secretkey is None:
        args.secretkey = os.getenv("AWS_S3_SECRET_KEY")
    if args.accesskey is None:
        args.accesskey = os.getenv("AWS_S3_ACCESS_KEY")

    if args.command == 'get':
        cache_get(args)
    elif args.command == 'set':
        cache_set(args)


if __name__ == '__main__':
    main()
