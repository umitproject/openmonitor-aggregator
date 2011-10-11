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

import datetime
import logging

from decimal import Decimal

from django.views.decorators.csrf import csrf_protect
from django.utils import simplejson as json
from django.http import HttpResponse

from geoip.models import IPRange, Location, LocationNamesAggregation


def save_geoip(request):
    geoip = json.loads(request.POST['geoip'])
    
    for gip in geoip:
        logging.critical(gip)
        
        gip['country_name'] = gip['country_name'] if gip['country_name'] is not None else ''
        
        location = Location.objects.filter(id=gip['loc_id'])
        if not location:
            location = Location()
            location.id = gip['loc_id']
            location.name = "%s, %s" % (gip['city'], gip['country_name']) if gip['city'] != '' else gip['country_name']
            location.country = gip['country_name']
            location.country_code = gip['country_code']
            location.state_region = gip['state_region']
            location.city = gip['city']
            location.zipcode = gip['zipcode']
            location.lat = Decimal(gip['latitude']) if gip['latitude'] != '' else Decimal("0.0")
            location.lon = Decimal(gip['longitude']) if gip['longitude'] != '' else Decimal("0.0")
            location.save()
            
        ip = IPRange()
        ip.location_id = gip['loc_id']
        ip.start_number = gip['start_number']
        ip.end_number = gip['end_number']
        ip.name = "%s, %s" % (gip['city'], gip['country_name']) if gip['city'] != '' else gip['country_name']
        ip.country = gip['country_name']
        ip.country_code = gip['country_code']
        ip.state_region = gip['state_region']
        ip.city = gip['city']
        ip.zipcode = gip['zipcode']
        ip.lat = Decimal(gip['latitude']) if gip['latitude'] != '' else Decimal("0.0")
        ip.lon = Decimal(gip['longitude']) if gip['longitude'] != '' else Decimal("0.0")
        
        print ip.lat, ip.lon
        logging.critical("%s, %s" % (ip.lat, ip.lon))
        
        ip.save()
        
        ############################################################
        # TODO: Make sure to create a COUNTRY entry for this range #
        ############################################################
    
    return HttpResponse('ADDED %s' % len(geoip))


@csrf_protect
def ajax_locations(request):
    if request.is_ajax() and request.GET.get('prefix', False):
        return HttpResponse(json.dumps(LocationNamesAggregation.get_names(request.GET['prefix'])))
    return HttpResponse(json.dumps([]))

