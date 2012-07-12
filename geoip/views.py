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
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

from gui.decorators import staff_member_required
from geoip.models import *
from geoip.forms import BanNetworkForm
from geoip.ip import convert_ip


@csrf_protect
def ajax_locations(request):
    if request.is_ajax() and request.GET.get('prefix', False):
        return HttpResponse(json.dumps(LocationNamesAggregation.get_names(request.GET['prefix'])))
    return HttpResponse(json.dumps([]))


@staff_member_required
def ban_network(request):
    form = BanNetworkForm(request.POST)
    msg = ""
    error = False
    
    if form.is_valid():
        network, created = IPRange.objects.get_or_create(\
                            start_number=convert_ip(form.cleaned_data['start_ip']),
                            end_number=convert_ip(form.cleaned_data['end_ip']),
                            defaults=dict(location_id = UNKNOWN_LOCATION.id,
                                          name = UNKNOWN_LOCATION.fullname,
                                          country_name = UNKNOWN_LOCATION.country_name,
                                          country_code = UNKNOWN_LOCATION.country_code,
                                          state_region = UNKNOWN_LOCATION.state_region,
                                          city = UNKNOWN_LOCATION.city,
                                          zipcode = UNKNOWN_LOCATION.zipcode,
                                          lat = UNKNOWN_LOCATION.lat,
                                          lon = UNKNOWN_LOCATION.lon))
        
        try:
            network.ban(BAN_FLAGS.get(form.cleaned_data['flag']))
        except Exception, err:
            error = str(err)
            msg = "Failed to ban network %s->%s with flag %s" % \
                                        (form.cleaned_data['start_ip'],
                                         form.cleaned_data['end_ip'],
                                         form.cleaned_data['flag'])
        else:
            msg = "Banned network %s->%s with flag %s successfuly!" % \
                                        (form.cleaned_data['start_ip'],
                                         form.cleaned_data['end_ip'],
                                         form.cleaned_data['flag'])
        
    form = BanNetworkForm()
    return render_to_response('geoip/ban_network.html', locals())
    







