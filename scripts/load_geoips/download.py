#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Author: Adriano Monteiro Marques <adriano@umitproject.org>
##
## Copyright (C) 2011 S2S Network Consultoria e Tecnologia da Informacao LTDA
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

import urllib2
import sys
import zipfile
import csv
import json
import urllib
import codecs

from os.path import join, dirname, exists

CUR_DIR = dirname(__file__)
GEO_FILE_ZIP = "GeoLiteCity_20120807.zip"
GEO_EXTRACT_DIR = "GeoLiteCity_20120807"
GEO_BLOCK_CSV = "%s/GeoLiteCity-Blocks.csv" % GEO_EXTRACT_DIR
GEO_LOCATION_CSV = "%s/GeoLiteCity-Location.csv" % GEO_EXTRACT_DIR
GEO_LITE = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCity_CSV/" + GEO_FILE_ZIP 


def downloader(url, fpath):
    request = urllib2.Request(url)
    _retriever(urllib2.urlopen(request), fpath)


def _retriever(urlfile, fpath):
    chunk = 4096
    f = open(fpath, "w")
    print "Downloading to %s" % fpath
    while 1:
        data = urlfile.read(chunk)
        if not data:
            print "Download to %s is done." % fpath
            break
        f.write(data)
        print "Read %s bytes" % len(data)


def download():
    if exists(join(CUR_DIR, GEO_FILE_ZIP)):
        if exists(join(CUR_DIR, GEO_BLOCK_CSV)) and exists(join(CUR_DIR, GEO_LOCATION_CSV)):
            return
    else:
        downloader(GEO_LITE, GEO_FILE_ZIP)

    zip = zipfile.ZipFile(join(CUR_DIR, GEO_FILE_ZIP))
    zip.extract(GEO_BLOCK_CSV)
    zip.extract(GEO_LOCATION_CSV)


if __name__ == "__main__":
    download()
#    load_data()
