#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## Author: Orcun Avsar <orc.avs@gmail.com>
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
"""Module for ajax autocomplete lookups for locations.
"""

from ajax_select import LookupChannel

from geoip.models import Location
from django.db.models import Q


class LocationLookup(LookupChannel):

  model = Location

  def get_query(self, q, request):
    words = q.replace(',', ' ').split()

    if not words:
        return []

    query = None
    for word in words:
        if not query:
            query = Q(city__istartswith=word)
        else:
            query = query | Q(city__istartswith=word)

    for word in words:
        query = query | Q(country_name__istartswith=word)

    return Location.objects.filter(query).distinct()[:20]


  def format_match(self,obj):
    return self.format_item_display(obj)


  def format_item_display(self, obj):
    return obj.fullname


  def get_result(self, obj):
    return obj.fullname
