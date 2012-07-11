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

"""Standalone script for filling ipranges.
"""

import csv
import sys
sys.path.insert(0, "/home/orcun/projects/openmonitor/aggregator/")

from django.core.management import setup_environ
import settings
setup_environ(settings)

from geoip.models import Location, IPRange


def fill_ip_ranges():

    counter = 0
    skipped = 0
    total = IPRange.objects.all().count()
    for ip_range in IPRange.objects.all():
        if (counter % 1000 == 0):
            print "Filled %s objects." % counter
            print "Skipped %s objects." % skipped
        counter += 1

        try:
            location = Location.objects.get(id=ip_range.location_id)
        except Location.DoesNotExist:
            skipped += 1
            continue
        ip_range.name = location.fullname
        ip_range.country_name = location.country_name
        ip_range.country_code = location.country_code
        ip_range.state_region = location.state_region
        ip_range.city = location.city
        ip_range.zipcode = location.zipcode
        ip_range.lat = location.lat
        ip_range.lon = location.lon
        ip_range.save()


if __name__ == '__main__':
    fill_ip_ranges()
