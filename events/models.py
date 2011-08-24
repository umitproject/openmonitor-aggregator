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
    targetType        = models.PositiveSmallIntegerField()
    eventType         = models.PositiveSmallIntegerField()
    firstDetectionUTC = models.DateTimeField()
    lastDetectionUTC  = models.DateTimeField()
    target            = models.TextField()
    active            = models.BooleanField()    # indicate if the event is still happening

    @staticmethod
    def getActiveEvents(limit=0):
        #return self.activated==True
        # TODO: order by firstDetection or lastDetection ?
        query = Event.objects.filter(active=True)#.order_by(lastDetectionUTC)
        if limit>0:
            query = query[:limit]
        return query

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

    def getTargetType(self):
        return TargetType.getTargetType(self.targetType)

    def getEventType(self):
        return EventType.getEventType(self.eventType)

    def getDict(self):

        locations = []
        for location in self.eventlocation_set.all():
            locations.append({'city': location.city, 'country': location.country, 'lat': location.latitude, 'lng': location.longitude})

        event = {
          'url': "/events/" + str(self.id),
          'targetType': self.getTargetType(),
          'target': self.target,
          'type': self.getEventType(),
          'firstdetection': self.firstDetectionUTC.ctime(),
          'lastdetection': self.lastDetectionUTC.ctime(),
          'active': self.active,
          'locations': locations
        }
        return event

    def getFullDict(self):
        event = self.getDict()

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