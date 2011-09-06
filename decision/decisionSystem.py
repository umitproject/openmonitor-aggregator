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

from events.models import *
from reports.models import *
from notificationsystem.system import NotificationSystem
import datetime, logging, random

class DecisionSystem:
    def newReport(report):
        # TODO: decision about event creation
        # for now event is created directly from report

        logging.info("Report received in decision system")

        event = Event()
        event.firstDetectionUTC = datetime.datetime.now()
        event.lastDetectionUTC  = datetime.datetime.now()

        if isinstance(report, WebsiteReport):
            event.target = report.url
            event.targetType = TargetType.Website
        elif isinstance(report, ServiceReport):
            event.target = report.serviceName
            event.targetType = TargetType.Service
        else:
            raise TypeError, 'report not supported'

        event.active = True

        # TODO: get correct event type
        event.eventType = EventType.Offline

        # save event
        event.save()

        # TODO: get isp information
        # TODO: save information about target server

        try:

            # get blocked node from trace
            if report.traceRoute:
                ip = report.traceRoute.getBlockedNode().ip

                # TODO: get geolocation information
                blockedNode = EventBlockedNode()
                blockedNode.ip = ip
                blockedNode.city = "Unknown"
                blockedNode.country = "Unknown"
                blockedNode.latitude = random.randrange(-90,90,1)
                blockedNode.longitude = random.randrange(0,180,1)
                blockedNode.event = event
                blockedNode.save()

            # associate report to event
            if isinstance(report, WebsiteReport):
                eventReport = EventWebsiteReport(event=event, report=report)
                eventReport.save()
            elif isinstance(report, ServiceReport):
                eventReport = EventServiceReport(event=event, report=report)
                eventReport.save()

            # save event location
            # TODO: get location from agent ip
            eventLocation = EventLocation()
            eventLocation.city = "Unknown"
            eventLocation.country = "Unknown"
            eventLocation.latitude = random.randrange(-90,90,1)
            eventLocation.longitude = random.randrange(0,180,1)
            eventLocation.event = event
            eventLocation.save()

        except Exception,ex:
            logging.error(ex)

        # report event no notification system
        NotificationSystem.publishEvent(event)


    newReport = staticmethod(newReport)

  