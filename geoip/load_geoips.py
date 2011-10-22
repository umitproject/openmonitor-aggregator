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
GEO_FILE_ZIP = "GeoLiteCity_20110906.zip"
GEO_EXTRACT_DIR = "GeoLiteCity_20110906"
GEO_BLOCK_CSV = "GeoLiteCity_20110906/GeoLiteCity-Blocks.csv"
GEO_LOCATION_CSV = "GeoLiteCity_20110906/GeoLiteCity-Location.csv"
COUNTRY_CODE_CSV = "country_codes.csv"
GEO_LITE = "http://geolite.maxmind.com/download/geoip/database/GeoLiteCity_CSV/" + GEO_FILE_ZIP 
BATCH_SIZE = 20
SAVE_GEOIP_URL = "http://localhost:9000/geoip/save_geoip/"


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

def lookup_location(id):
    locations = unicode_reader(open(join(CUR_DIR, GEO_LOCATION_CSV), 'rUb'), delimiter=',')
    for row in locations:
        if id == row[0]:
            return row

def lookup_country_name(country_code):
    countries = csv.reader(open(join(CUR_DIR, COUNTRY_CODE_CSV), 'rUb'), delimiter=';')
    for row in countries:
        if country_code.upper() == row[1]:
            if row[1].upper() == "KR":
                return "South Korea"
            elif row[1].upper() == "KP":
                return "North Korea"
            
            return row[0].split(',')[0].capitalize()

def load_data():
    print "Loading data..."
    csv.field_size_limit(1000000000)
    entries = csv.reader(open(join(CUR_DIR, GEO_BLOCK_CSV), 'rUb'))
    
    num = 0
    batch = []
    print "Sending data..."
    for row in entries:
        if num <= 1:
            # In order to skip the headers
            num += 1
            continue
        
        print "Sending %s #%s..." % (row[2], num),
        if len(batch) >= BATCH_SIZE:
            print urllib.urlopen(SAVE_GEOIP_URL,
                         urllib.urlencode(\
                                      dict(geoip=json.dumps(batch)))).read()
            batch=[]
        
        loc = lookup_location(row[2])
        batch.append(dict(loc_id=row[2],
                          start_number=row[0],
                          end_number=row[1],
                          country_name=lookup_country_name(loc[1]),
                          country_code=loc[1],
                          state_region=loc[2],
                          city=loc[3],
                          zipcode=loc[4],
                          latitude=loc[5],
                          longitude=loc[6]))
        
        num += 1
    

def load_cities():
    pass


def unicode_reader(csv_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(csv_data, dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'latin1') for cell in row]


if __name__ == "__main__":
    download()
    load_data()