#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Author: Adriano Monteiro Marques <adriano@umitproject.org>
## Author: Orcun Avsar <orc.avs[at]gmail.com>
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

"""Standalone script for filling country names and updating fullnames.
"""

import csv
import sys
from os.path import dirname, abspath

AGG_DIR =  dirname(dirname(dirname(abspath(__file__))))
sys.path.insert(0, AGG_DIR)

from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.db import connection, transaction
from django.db import connections

from geoip.models import Location


CSV_FILE = 'country_codes.csv'


def fill_country_names():

    def fill(iterable):
        for ln in iterable:
            country_name, country_code = ln
            country_name = country_name.split(',')[0]
            print "Updating country %s" % country_name
            Location.objects.filter(country_code=country_code).update(country_name=country_name.title())

    countries = csv.reader(open(CSV_FILE, 'r'), delimiter=';')
    fill(countries)

    extra = [('South Korea', 'KR'), ('North Korea', 'KP'),
             ('British Virgin Islands', 'VG'), ('U.S. Virgin Islands', 'VI')]
    fill(extra)


def fill_fullnames():
    counter = 0
    total = Location.objects.all().count()
    for location in Location.objects.all():
        if (counter % 1000 == 0):
            print "Filled %s objects." % counter
        counter += 1

        if location.country_code == 'UN':
            continue

        if location.city:
            location.fullname = "%s, %s" % (location.city,location.country_name)
        else:
            location.fullname = location.country_name

        location.save()




if __name__ == '__main__':
    if '--country-names' in sys.argv:
        fill_country_names()
    if '--fullnames' in sys.argv:
        fill_fullnames()
