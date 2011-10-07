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

from django.db import models
from django.utils import simplejson
from django.core.cache import cache

from geoip.models import Location

EVENT_CACHE_TIME = 30 # Leave it cached for half a minute
LOCATION_CACHE_TIME = 60*10 # Cache it for 10 minutes
EVENT_LIST_CACHE_KEY = "events_list"
LOCATION_CACHE_KEY = "location_%s"

eventType = ["Censor", "Throttling", "Offline"]
targetType = ["Website", "Service"]

class EventType:
    Censor, Throttling, Offline = range(3)

    @staticmethod
    def getEventType(id):
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
    def getTargetType(id):
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
    active = models.BooleanField() # indicate if the event is still happening
    
    ############################################################################
    # We need to keep the basic region data here to make it faster to retrieve.
    # Keeping data away from where it is used is a huge waste of resources on
    # GAE and can severely constraint its scaleability
    location_ids = models.TextField()
    location_names = models.TextField()
    location_country_names = models.TextField()
    location_country_codes = models.TextField()
    lats = models.DecimalField(decimal_places=20, max_digits=23)
    lons = models.DecimalField(decimal_places=20, max_digits=23)
    
    
    @property
    def location(self):
        location = cache.get(LOCATION_CACHE_KEY % self.location_id, False)
        if not location:
            region = Location.objects.get(id=self.location_id)
            cache.set(LOCATION_CACHE_KEY % self.location_id, LOCATION_CACHE_TIME)
        
        return location

    @staticmethod
    def get_active_events(limit=20):
        """This method must be cached to save some processing and access to the
        datastore. The cache is invalidated as soon as new events are registered
        so we don't miss them showing up in real time.
        """
        # TODO: order by firstDetection or lastDetection ?
        events = cache.get(EVENT_LIST_CACHE_KEY, False)
        if not events:
            events = Event.objects.filter(active=True).order_by("last_detection_utc")[:limit]
            cache.set(EVENT_LIST_CACHE_KEY, events, EVENT_CACHE_TIME)
        
        return events
    
    
    # TODO: more search methods:
    #   search by location (should be the name of place or coordinates ?
    #   search by isp ?
    #   search events for specific website
    #   search events for specific services
    #   search old events too, limited by dates

    # get all the active events, in a location, and for a specific website/service
    #@staticmethod
    #def getActiveEvents(location, target):
    #    pass


    #def __unicode__(self):
    #    return u'%s %s %s' % (self.targetType, self.eventType, self.firstDetectionUTC)

    #def __str__(self):
    #    return '%s %s %s' % (self.targetType, self.eventType, self.firstDetectionUTC)

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
          'location': {'region_id':self.region_id,
                       'name': self.region_name,
                       'country': self.region_country_code,
                       'lat': self.lat,
                       'lng': self.lon}
        }
        
        return event

    def get_full_dict(self):
        event = self.get_dict()

        isps = []
        for isp in self.eventisp_set.all():
            isps.append(isp.isp)

        blockedNodes = []
        for blockedNode in self.eventblockednode_set.all():
            blockedNodes.append({'city': blockedNode.city, 'country': blockedNode.country, 'lat': blockedNode.latitude, 'lng': blockedNode.longitude, 'ip': blockedNode.ip})

        event['isps'] = isps
        event['blockingNodes'] = blockedNodes
        return event


class Location(models.Model):
    city     = models.CharField(max_length=100)
    country  = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude= models.FloatField()

    class Meta:
        abstract = True


class EventLocation(Location):
    event    = models.ForeignKey('Event')


class EventISP(models.Model):
    event = models.ForeignKey('Event')
    isp   = models.CharField(max_length=100)


class EventWebsiteReport(models.Model):
    event  = models.ForeignKey('Event')
    report = models.ForeignKey('reports.WebsiteReport')


class EventServiceReport(models.Model):
    event  = models.ForeignKey('Event')
    report = models.ForeignKey('reports.ServiceReport')

    
class EventBlockedNode(Location):
    event = models.ForeignKey('Event')
    ip    = models.CharField(max_length=255)