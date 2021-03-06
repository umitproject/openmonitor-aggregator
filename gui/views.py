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
import logging
import decimal

import simplejson as json

from django.shortcuts import render_to_response
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.core.urlresolvers import reverse

from gui.forms import SuggestServiceForm, SuggestWebsiteForm, WebsiteEventForm, ServiceEventForm
from gui.decorators import staff_member_required
from geoip.models import Location
from suggestions.models import WebsiteSuggestion, ServiceSuggestion
from events.models import Event, EventLocationAggregation, TargetType, EventType
from reports.models import WebsiteReport
from notificationsystem.system import NotificationSystem
from filetransfers.api import serve_file


# Our current limit is 25. Let's play around with this and we'll figure if it is enough
SHOW_EVENT_LIMIT = 25

# View cache is set to 10 minutes now. We'll slowly decrease this with time to test
VIEW_CACHE_TIME = 60 * 10


def home(request):
    return map(request)


def map(request):
    initialEvents = EventLocationAggregation.get_active_aggregated_events_as_json()
    #initialEvents = Event.get_active_events_as_json(SHOW_EVENT_LIMIT)
    print initialEvents
    return render_to_response('notificationsystem/map.html',
                              {'initial_events': initialEvents},
                              context_instance=RequestContext(request))


def realtimebox(request):
    initialEvents = EventLocationAggregation.get_active_aggregated_events_as_json()
    #initialEvents = Event.get_active_events_as_json(SHOW_EVENT_LIMIT)
    print initialEvents
    return render_to_response('notificationsystem/realtimebox.html',
                              {'initial_events': initialEvents},
                              context_instance=RequestContext(request))


def poll_active_events(request):
    """Returns json response of new events to AJAX caller.
    """
    events = EventLocationAggregation.get_active_aggregated_events_as_json()
    #events = Event.get_active_events_as_json(SHOW_EVENT_LIMIT)
    return HttpResponse(events)


def event(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise Http404

    event = event.get_full_dict()
    
    #blockingNodes = json.dumps(eventDict['blockingNodes'])
    
    event_json = json.dumps([event], use_decimal=True)
    countries = {}
    for location in event['locations']:
      country_name = location['location_country_name']
      if not countries.has_key(country_name):
        countries[country_name] = []
        
      if country_name != 'Unknown':
        location_name = location['location_name']  
        if location_name != 'Unknown':
          if not location_name in countries[country_name]:
            countries[country_name].append(location_name)
        
    num_of_reports = len(event['locations'])
    return render_to_response('events/event.html',
                              {'countries': countries,
                               'num_of_reports': num_of_reports,
                               'event': event,
                               'event_json': event_json},
                              context_instance=RequestContext(request))

def ajax_event_traces(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    event_traces = event.get_latest_traces_as_json()
    return HttpResponse(event_traces)


def about(request):
    user = request.user
    return render_to_response('gui/about.html', locals(), context_instance=RequestContext(request))


def suggest_service(request):
    if request.POST:
        form = SuggestServiceForm(request.POST)
        form.init_repeat_check(request, SuggestServiceForm,
                               ['service_name', 'host_name',
                                'port', 'location'])
        if form.is_valid():
            data = form.cleaned_data
            host_name = data['host_name']
            service_name = data['service_name']
            port = data['port']
            location = data['location']

            location_id = location and location.id or None

            if request.user.is_authenticated:
                user_id = request.user.id
            else:
                user_id = None

            ServiceSuggestion(host_name=host_name,
                              service_name=service_name,
                              port=port,
                              user_id=user_id,
                              location_id=location_id).save()

            if request.user.is_authenticated():
                messages.add_message(request, messages.SUCCESS,
                                     "Suggestion added successfully.")
            return HttpResponseRedirect(reverse('suggest_service'))
    else:
        form = SuggestServiceForm()

    return render_to_response('gui/suggest_service.html', locals(), context_instance=RequestContext(request))


def suggest_website(request):
    if request.POST:
        form = SuggestWebsiteForm(request.POST)
        form.init_repeat_check(request, SuggestWebsiteForm,
                              ['website', 'location'])
        if form.is_valid():
            data = form.cleaned_data
            website_url = data['website']
            location = data['location']

            location_id = location and location.id or None

            if request.user.is_authenticated:
                user_id = request.user.id
            else:
                user_id = None

            WebsiteSuggestion(website_url=website_url,
                              location_id=location_id,
                              user_id=user_id).save()

            if request.user.is_authenticated():
                messages.add_message(request, messages.SUCCESS,
                                     "Suggestion added successfully.")
            return HttpResponseRedirect(reverse('suggest_website'))
    else:
        form = SuggestWebsiteForm()

    return render_to_response('gui/suggest_website.html', locals(), context_instance=RequestContext(request))


def create_website_event(request):
    if request.method == 'POST':
        form = WebsiteEventForm(request.POST)
        if form.is_valid():
            website = form.cleaned_data['website']
            first_detection = form.cleaned_data['first_detection']
            event_type = form.cleaned_data['event_type']
            location = Location.retrieve_location(form.cleaned_data['location'].split(', ')[0])

            logging.info(location)

            event = Event()
            event.active = True
            if first_detection:
                event.first_detection_utc = first_detection
            else:
                event.first_detection_utc = datetime.datetime.now()
            event.last_detection_utc  = datetime.datetime.now()
            event.target = website
            event.target_type = TargetType.Website
            if event_type:
                # 'censor', 'throttling', 'offline'
                if event_type == 'censor':
                    event.event_type = EventType.Censor
                elif event_type == 'throttling':
                    event.event_type = EventType.Throttling
                else:
                    event.event_type = EventType.Offline
            else:
                event.event_type = EventType.Offline

            logging.info(location)

            if location!=None:
                event.location_ids.append(location.id)
                event.location_names.append(location.fullname)
                event.location_country_names.append(location.country_name)
                event.location_country_codes.append(location.country_code)
                event.lats.append(location.lat)
                event.lons.append(location.lon)
                event.isps.append('')

            event.save()
            NotificationSystem.publishEvent(event)

            return HttpResponse(json.dumps(dict(status='OK',
                       msg='Website event added successfully!',
                       errors=None)))
        else:
            return HttpResponse(json.dumps(dict(status='FAILED',
                    msg='Failed to add event.',
                    errors=form.errors)))
    
    form = WebsiteEventForm()
    return render_to_response('gui/create_website_event.html', locals(), context_instance=RequestContext(request))


def create_service_event(request):
    if request.method == 'POST':
        form = ServiceEventForm(request.POST)
        if form.is_valid():
            service = form.cleaned_data['service']
            first_detection = form.cleaned_data['first_detection']
            event_type = form.cleaned_data['event_type']
            location = Location.retrieve_location(form.cleaned_data['location'].split(', ')[0])

            event = Event()
            event.active = True
            if first_detection:
                event.first_detection_utc = first_detection
            else:
                event.first_detection_utc = datetime.datetime.now()
            event.last_detection_utc  = datetime.datetime.now()
            event.target = service
            event.target_type = TargetType.Service
            if event_type:
                # 'censor', 'throttling', 'offline'
                if event_type == 'censor':
                    event.event_type = EventType.Censor
                elif event_type == 'throttling':
                    event.event_type = EventType.Throttling
                else:
                    event.event_type = EventType.Offline
            else:
                event.event_type = EventType.Offline

            if location!=None:
                event.location_ids.append(location.id)
                event.location_names.append(location.fullname)
                event.location_country_names.append(location.country_name)
                event.location_country_codes.append(location.country_code)
                event.lats.append(location.lat)
                event.lons.append(location.lon)
                event.isps.append('')

            event.save()
            NotificationSystem.publishEvent(event)

            return HttpResponse(json.dumps(dict(status='OK',
                       msg='Website event added successfully!',
                       errors=None)))
        else:
            return HttpResponse(json.dumps(dict(status='FAILED',
                    msg='Failed to add event.',
                    errors=form.errors)))

    form = ServiceEventForm()
    return render_to_response('gui/create_service_event.html', locals(), context_instance=RequestContext(request))


def serve_media(request, id):
    upload = get_object_or_404(WebsiteReport, pk=id)
    return serve_file(request, upload.file)


@staff_member_required
def ban_agent(request):
    
    return render_to_response('gui/ban_agent.html', locals(), context_instance=RequestContext(request))


@staff_member_required
def ban_network(request):
    
    return render_to_response('gui/ban_network.html', locals(), context_instance=RequestContext(request))


def manifesto(request):
    """This is our manifesto on how should Open Monitor should be used and
    we expect people to respect our restrictions in recognition of the time
    we've being devoting to develop and support this powerful tool.
    """
    return render_to_response("gui/manifesto.html", locals(), context_instance=RequestContext(request))
