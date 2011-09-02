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

from django.shortcuts import render_to_response
from django.utils import simplejson
from google.appengine.api import channel
from events.models import Event

def map(request):
    token = channel.create_channel('map')
    events = Event.getActiveEvents()
    events_dict = []
    for event in events:
        events_dict.append(event.getDict())
    initialEvents = simplejson.dumps(events_dict)
    return render_to_response('notificationsystem/map.html', {'token': token, 'initial_events': initialEvents})

def realtimebox(request):
    token = channel.create_channel('realtimebox')
    events = Event.getActiveEvents()
    events_dict = []
    for event in events:
        events_dict.append(event.getDict())
    initialEvents = simplejson.dumps(events_dict)
    return render_to_response('notificationsystem/realtimebox.html', {'token': token, 'initial_events': initialEvents})

def event(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise Http404
    eventDict = event.getFullDict()
    locations = simplejson.dumps(eventDict['locations'])
    blockingNodes = simplejson.dumps(eventDict['blockingNodes'])

    return render_to_response('events/event.html', {'eventInfo': eventDict, 'locations': locations, 'blockingNodes': blockingNodes})