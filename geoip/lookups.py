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
from geoip.models import LocationNamesAggregation


class LocationLookup(LookupChannel):

  model = Location
  
  def get_query(self,q,request):
    words = q.replace(',',' ').replace('-', ' ').split()
    query = Location.objects.all()
    
    queries = []
    for word in words:
      query = Location.objects.filter(name__icontains=word)[:20]
      queries.append(query)
    
    entities = []
    for query in queries:
      for entity in query:
        entities.append(entity)
    
    return entities
  
  def format_match(self,obj):
    obj.name