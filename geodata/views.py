#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Author: Adriano Monteiro Marques <adriano@umitproject.org>
## Author: Diogo Pinheiro <diogormpinheiro@gmail.com>
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

import datetime

from decimal import Decimal

from django.views.decorators.csrf import csrf_protect
from django.utils import simplejson as json
from django.http import HttpResponse

from geodata.models import Region, RegionNamesAggregation


def save_geoname(request):
    geoname = json.loads(request.POST['geoname'])
    
    geon = Region.objects.filter(name=geoname['name'])
    if geon:
        if geon[0].id != geoname['id']:
            geon[0].id = geoname['id']
            geon[0].save()
        return HttpResponse('REPEATED')
    
    g = Region()
    g.id = geoname['id']
    g.name = geoname['name']
    g.asciiname = geoname['asciiname']
    g.alternatenames = geoname['alternatenames']
    g.lat = Decimal(geoname['latitude'])
    g.lon = Decimal(geoname['longitude'])
    g.feature_class = geoname['feature_class']
    g.feature_code = geoname['feature_code']
    g.country_code = geoname['country_code']
    g.cc2 = geoname['cc2']
    g.population = int(geoname['population']) if geoname['population'] else 0
    g.elevation = int(geoname['elevation']) if geoname['elevation'] else 0
    g.gtopo30 = int(geoname['gtopo30']) if geoname['gtopo30'] else 0
    g.modification_date = datetime.datetime(*[int(d) for d in geoname['modification_date'].split('-')])
    g.save()
    
    return HttpResponse('OK')


@csrf_protect
def ajax_regions(request):
    if request.is_ajax() and request.GET.get('prefix', False):
        return HttpResponse(json.dumps(RegionNamesAggregation.get_names(request.GET['prefix'])))
    return HttpResponse(json.dumps([]))



