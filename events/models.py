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

import decimal
import simplejson as json

from django.db import models
from django.utils import simplejson
from django.core.cache import cache

from geoip.models import Location
from dbextra.fields import ListField
import logging

SINGLE_EVENT_CACHE_TIME = 30
EVENT_CACHE_TIME = 30 # Leave it cached for half a minute
LOCATION_CACHE_TIME = 60*10 # Cache it for 10 minutes
EVENT_LIST_CACHE_KEY = "events_list"
LOCATION_CACHE_KEY = "location_%s"
EVENT_CACHE_KEY = 'event_%s'


eventType = ["Censor", "Throttling", "Offline"]
targetType = ["Website", "Service"]

class EventType:
    Censor, Throttling, Offline = range(3)

    @staticmethod
    def get_event_type(id):
        if id==EventType.Censor:
            return "Censor"
        elif id==EventType.Throttling:
            return "Throttling"
        elif id==EventType.Offline:
            return "Offline"
        else:
            return "Unknown"

class TargetType:
    Website, Service = range(2)

    @staticmethod
    def get_target_type(id):
        if id==TargetType.Website:
            return "Website"
        elif id==TargetType.Service:
            return "Service"
        else:
            return "Unknown"


class Event(models.Model):
    target_type = models.PositiveSmallIntegerField()
    event_type = models.PositiveSmallIntegerField()
    first_detection_utc = models.DateTimeField()
    last_detection_utc = models.DateTimeField()
    target = models.TextField()
    status_code = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True) # indicate if the event is still happening
    
    ############################################################################
    # We need to keep the basic region data here to make it faster to retrieve.
    # Keeping data away from where it is used is a huge waste of resources on
    # GAE and can severely constraint its scaleability
    location_ids = ListField(py_type=int)
    location_names = ListField()
    location_country_names = ListField()
    location_country_codes = ListField()
    lats = ListField(py_type=decimal.Decimal)
    lons = ListField(py_type=decimal.Decimal)
    isps = ListField()
    
    # List of each containing report's of trace
    latest_traces = ListField(py_type=str, max_size=100)

    @property
    def locations(self):
        locations = []
        for location_id in self.location_ids:
            location = cache.get(LOCATION_CACHE_KEY % location_id, False)
            if not location:
                location = Location.get_location_or_unknown(id=location_id)
                cache.set(LOCATION_CACHE_KEY % location_id, location, LOCATION_CACHE_TIME)
            locations.append(location)
        return locations

    @staticmethod
    def get_active_events(limit=20):
        """This method must be cached to save some processing and access to the
        datastore. The cache is invalidated as soon as new events are registered
        so we don't miss them showing up in real time.
        """
        events = cache.get(EVENT_LIST_CACHE_KEY, False)
        if not events:
            events = Event.objects.filter(active=True).order_by("last_detection_utc")[:limit]
            cache.set(EVENT_LIST_CACHE_KEY, events, EVENT_CACHE_TIME)
        
        return events

    @staticmethod
    def get_active_events_as_json(limit=20):
        events = Event.get_active_events(limit)
        events_dict = []
        for event in events:
            events_dict.append(event.get_dict())
        initialEvents = json.dumps(events_dict, use_decimal=True)
        return initialEvents

    @staticmethod
    def get_active_events_region(regions, limit=20):
        result = []
        for country_code in regions:
            locationagg = EventLocationAggregation.objects.filter(location_country_code__exact=country_code).order_by("last_detection_utc")[:limit]
            if len(locationagg)>0:
                result.extend(locationagg[0].get_events())
        return result
    
    def get_target_type(self):
        return TargetType.get_target_type(self.target_type)

    def get_event_type(self):
        return EventType.get_event_type(self.event_type)

    def get_dict(self):
        event = {
          'url': "/events/" + str(self.id),
          'targetType': self.get_target_type(),
          'target': self.target,
          'type': self.get_event_type(),
          'firstdetection': self.first_detection_utc.ctime(),
          'lastdetection': self.last_detection_utc.ctime(),
          'active': self.active,
          'locations': [dict((('location_id', locset[0]),
                          ('location_name', locset[1]),
                          ('location_country_name', locset[2]),
                          ('location_country_code', locset[3]),
                          ('lat', locset[4]),
                          ('lon', locset[5]),
                          ('isp', locset[6]))) for locset in zip(self.location_ids,
                                                                 self.location_names,
                                                                 self.location_country_names,
                                                                 self.location_country_codes,
                                                                 self.lats,
                                                                 self.lons,
                                                                 self.isps)]
        }
        
        return event

    def get_full_dict(self):
        event = self.get_dict()
        
        # TODO: Refer to decision/decisionSystem.py:68 for code to generate this data.
        #for blockedNode in self.eventblockednode_set.all():
        #    blockedNodes.append({'city': blockedNode.city, 'country': blockedNode.country, 'lat': blockedNode.latitude, 'lng': blockedNode.longitude, 'ip': blockedNode.ip})

        event['isps'] = self.isps
        event['blockingNodes'] = []
        
        return event

    def get_latest_traces_as_json(self):
        #TODO(orc.avs): Cache the result
        return json.dumps([trace for trace in self.latest_traces])

    def save(self, *args, **kwargs):
        new = self.id is None

        res = super(Event, self).save(*args, **kwargs)

        if new:
            EventLocationAggregation.add_event(self)
        else:
            cache.delete(EVENT_CACHE_KEY % self.id)

        cache.delete(EVENT_LIST_CACHE_KEY)

        return res

    def __unicode__(self):
        return "Event in %s" % self.location_country_codes


class EventLocationAggregation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    
    location_country_code = models.CharField(max_length=2)
    events = ListField(py_type=str)
    count = models.IntegerField(default=1)


    # Event Replic 
    # For scalability reasons, we decided to replicate this data
    target_type = models.PositiveSmallIntegerField()
    event_type = models.PositiveSmallIntegerField()
    first_detection_utc = models.DateTimeField()
    last_detection_utc = models.DateTimeField(auto_now=True)
    target = models.TextField()
    status_code = models.IntegerField(null=True, blank=True)
    
    location_ids = ListField(py_type=int)
    location_names = ListField()
    location_country_names = ListField()
    location_country_codes = ListField()
    lats = ListField(py_type=decimal.Decimal)
    lons = ListField(py_type=decimal.Decimal)
    isps = ListField()
    
    # List of each containing report's of trace
    latest_traces = ListField(py_type=str, max_size=100)


    @staticmethod
    def add_event(event):
        for country_code in event.location_country_codes:
            agg = EventLocationAggregation.objects.filter(location_country_code__exact=country_code)
            add = False
            if agg:
                agg = agg[0]
                if event.id not in agg.events:
                    agg.count += 1
                    add = True
            else:
                agg = EventLocationAggregation()
                agg.location_country_code = country_code
                add = True


            # Update parameters of last event (to replica/cache)
            agg.target_type = event.target_type
            agg.event_type = event.event_type
            agg.first_detection_utc = event.first_detection_utc
            agg.last_detection_utc = event.last_detection_utc
            agg.target = event.target
            agg.status_code = event.status_code
            
            agg.location_ids = event.location_ids
            agg.location_names = event.location_names
            agg.location_country_names = event.location_country_names
            agg.location_country_codes = event.location_country_codes
            agg.lats = event.lats
            agg.lons = event.lons
            agg.isps = event.isps
            
            agg.latest_traces = event.latest_traces

            if add:
                agg.events.append(event.id)
                agg.save()

            # TODO: delete LOCATION_CACHE


    @staticmethod
    def get_active_events_as_json():
        events = EventLocationAggregation.get_active_events()
        events_dict = []
        for event in events:
            events_dict.append(event.get_dict())
        initialEvents = json.dumps(events_dict, use_decimal=True)
        return initialEvents

    @staticmethod
    def get_active_events():
        #events = cache.get(EVENT_LIST_CACHE_KEY, False)
        #if not events:
        events = EventLocationAggregation.objects.order_by("last_detection_utc")
        #    cache.set(EVENT_LIST_CACHE_KEY, events, EVENT_CACHE_TIME)
        return events

    created_at = models.DateTimeField(auto_now_add=True)
    last_detection_utc = models.DateTimeField(auto_now=True)
    location_country_code = models.CharField(max_length=2)
    events = ListField(py_type=str)
    count = models.IntegerField(default=1)

    def get_dict(self):
            event = {
              'targetType': self.get_target_type(),
              'target': self.target,
              'type': self.get_event_type(),
              'firstdetection': self.first_detection_utc.ctime(),
              'lastdetection': self.last_detection_utc.ctime(),
              'active': self.active,
              'locations': [dict((('location_id', locset[0]),
                              ('location_name', locset[1]),
                              ('location_country_name', locset[2]),
                              ('location_country_code', locset[3]),
                              ('lat', locset[4]),
                              ('lon', locset[5]),
                              ('isp', locset[6]))) for locset in zip(self.location_ids,
                                                                     self.location_names,
                                                                     self.location_country_names,
                                                                     self.location_country_codes,
                                                                     self.lats,
                                                                     self.lons,
                                                                     self.isps)]
            }
            
            return event

    def get_events(self):
        events = []
        for event_id in self.events:
            event = cache.get(EVENT_CACHE_KEY % event_id, False)
            if not event:
                event = Event.objects.get(id=event_id)
                cache.set(EVENT_CACHE_KEY % event_id, SINGLE_EVENT_CACHE_TIME)
            events.append(event)
        return events

    def __unicode__(self):
        return "Event in %s - %s" % (self.location_country_code, self.count)

