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
import decimal

import simplejson as json

from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404

from gui.decorators import staff_member_required

from geoip.models import Location
from suggestions.models import WebsiteSuggestion, ServiceSuggestion
from events.models import Event, TargetType, EventType


@staff_member_required
@never_cache
def generate_test_set(request):
    current_test_set = []
    website_suggestions = []
    service_suggestions = []
    
    
    
    return render_to_response('decision/generate_test_set.html', locals())






