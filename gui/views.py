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
from django.utils import simplejson as json
from django.http import HttpResponse, Http404
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404

from google.appengine.api import channel

from events.models import Event
from gui.forms import SuggestServiceForm, SuggestWebsiteForm
from gui.decorators import cant_repeat_form
from geoip.models import Location
from suggestions.models import WebsiteSuggestion, ServiceSuggestion
from reports.models import WebsiteReport
from filetransfers.api import serve_file


# Our current limit is 25. Let's play around with this and we'll figure if it is enough
SHOW_EVENT_LIMIT = 25

# View cache is set to 10 minutes now. We'll slowly decrease this with time to test
VIEW_CACHE_TIME = 60 * 10


def home(request):
    return map(request)


def map(request):
    token = channel.create_channel('map')
    
    # Our current limit 
    events = Event.get_active_events(SHOW_EVENT_LIMIT)
    events_dict = []
    for event in events:
        events_dict.append(event.getDict())
    initialEvents = json.dumps(events_dict)
    return render_to_response('notificationsystem/map.html', {'token': token, 'initial_events': initialEvents})


def realtimebox(request):
    token = channel.create_channel('realtimebox')
    events = Event.get_active_events(SHOW_EVENT_LIMIT)
    events_dict = []
    for event in events:
        events_dict.append(event.getDict())
    initialEvents = json.dumps(events_dict)
    return render_to_response('notificationsystem/realtimebox.html', {'token': token, 'initial_events': initialEvents})


def event(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise Http404
    eventDict = event.getFullDict()
    locations = json.dumps(eventDict['locations'])
    blockingNodes = json.dumps(eventDict['blockingNodes'])

    return render_to_response('events/event.html', {'eventInfo': eventDict, 'locations': locations, 'blockingNodes': blockingNodes})



def about(request):
    return render_to_response('gui/about.html', locals())


@cant_repeat_form(SuggestServiceForm, ['service_name', 'host_name', 'port', 'location'])
def suggest_service(request, form, valid, *args, **kwargs):
    if (form is not None) and valid:
        service_name = form.cleaned_data['service_name']
        host_name = form.cleaned_data['host_name']
        port = form.cleaned_data['port']
        location = Location.retrieve_location(form.cleaned_data['location'].split(', ')[0])
        
        suggestion = ServiceSuggestion()
        suggestion.service_name = service_name
        suggestion.host_name = host_name
        suggestion.port = port
        suggestion.location = location
        suggestion.save()
        
        return HttpResponse(json.dumps(dict(status='OK',
                   msg='Website suggestion added successfully! Make sure you \
subscribe to receive the site status once it is tested.',
                   errors=None)))
    elif (form is not None) and (not valid):
        return HttpResponse(json.dumps(dict(status='FAILED',
                   msg='Failed to add your suggestion. Please, make sure you \
provided all terms.',
                   errors=form.errors)))
    
    form = SuggestServiceForm()
    return render_to_response('gui/suggest_service.html', locals())


@cant_repeat_form(SuggestWebsiteForm, ['website', 'location'])
def suggest_website(request, form, valid, *args, **kwargs):
    if (form is not None) and valid:
        website = form.cleaned_data['website']
        location = Location.retrieve_location(form.cleaned_data['location'].split(', ')[0])
        
        suggestion = WebsiteSuggestion()
        suggestion.website_url = website
        suggestion.location = location
        suggestion.save()
        
        return HttpResponse(json.dumps(dict(status='OK',
                   msg='Website suggestion added successfully! Make sure you \
subscribe to receive the site status once it is tested.',
                   errors=None)))
    elif (form is not None) and (not valid):
        return HttpResponse(json.dumps(dict(status='FAILED',
                msg='Failed to add your suggestion. Please, make sure you \
provided at least a valid website.',
                errors=form.errors)))
    
    form = SuggestWebsiteForm()
    return render_to_response('gui/suggest_website.html', locals())


def serve_media(request, id):
    upload = get_object_or_404(WebsiteReport, pk=id)
    return serve_file(request, upload.file)
