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

from os.path import join, dirname, exists

CUR_DIR = dirname(__file__)
ALL_COUNTRIES = "http://download.geonames.org/export/dump/allCountries.zip"
ALL_CITIES = "http://download.geonames.org/export/dump/cities1000.zip"
BATCH_SIZE = 15
SAVE_GEONAME_URL = "http://localhost:9000/geodata/save_geoname/"


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

def download_allCountries():
    if exists(join(CUR_DIR, "allCountries.zip")):
        if exists(join(CUR_DIR, "allCountries.txt")):
            return
    else:
        downloader(ALL_COUNTRIES, 'allCountries.zip')
    
    zip = zipfile.ZipFile(join(CUR_DIR, "allCountries.zip"))
    zip.extract("allCountries.txt")

def download_allCities():
    if exists(join(CUR_DIR, "cities1000.zip")):
        if exists(join(CUR_DIR, "cities1000.txt")):
            return
    else:
        downloader(ALL_CITIES, 'cities1000.zip')
    
    zip = zipfile.ZipFile(join(CUR_DIR, "cities1000.zip"))
    zip.extract("cities1000.txt")

def load_countries():
    print "Loading countries..."
    csv.field_size_limit(1000000000)
    countries = csv.reader(open('allCountries.txt', 'rb'), delimiter='\t')
    
    num = 1
    print "Sending countries..."
    for row in countries:
        print "Sending %s #%s..." % (row[2], num),
        print urllib.urlopen(SAVE_GEONAME_URL,
                     urllib.urlencode(\
                            dict(geoname=json.dumps(dict(id=row[0],
                                                         name=row[1],
                                                         asciiname=row[2],
                                                         alternatenames=row[3],
                                                         latitude=row[4],
                                                         longitude=row[5],
                                                         feature_class=row[6],
                                                         feature_code=row[7],
                                                         country_code=row[8],
                                                         cc2=row[9],
                                                         admin1_code=row[10],
                                                         admin2_code=row[11],
                                                         admin3_code=row[12],
                                                         admin4_code=row[13],
                                                         population=row[14],
                                                         elevation=row[15],
                                                         gtopo30=row[16],
                                                         timezone=row[17],
                                                         modification_date=row[18]))))).read()
        num += 1
    

def load_cities():
    pass

if __name__ == "__main__":
    download_allCountries()
    load_countries()
    
    download_allCities()
    load_cities()
