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

from django.utils import simplejson as json

from events.models import *
from reports.models import *
from notificationsystem.system import NotificationSystem
import datetime, logging, random

REPORT_PERIOD = datetime.timedelta(days=1)


class DecisionSystem:
    def newReport(report):
        # TODO: decision about event creation
        # for now event is created directly from report

        logging.info("Report received in decision system")

        event = Event()
        event.first_detection_utc = datetime.datetime.now()
        event.last_detection_utc  = datetime.datetime.now()

        if isinstance(report, WebsiteReport):
            event.target = report.url
            event.target_type = TargetType.Website
        elif isinstance(report, ServiceReport):
            event.target = report.target
            event.target_type = TargetType.Service
        else:
            raise TypeError, 'report not supported'

        event.status_code = report.status_code
        if event.status_code not in [200, 301, 302]:
            event.active = True
        else:
            event.active = False

        # TODO: get correct event type
        event.event_type = EventType.Offline

        # TODO: get isp information
        # TODO: save information about target server

        try:
            event.location_ids.append(report.agent_location_id)
            event.location_names.append(report.agent_location_name)
            event.location_country_names.append(report.agent_country_name)
            event.location_country_codes.append(report.agent_country_code)
            event.lats.append(report.agent_lat)
            event.lons.append(report.agent_lon)

            # TODO: ISP!
            event.isps.append('')
            #isps = ListField()

            if len(report.trace):
                trace = [t.get_dict() for t in report.trace]
                trace_json = json.dumps(trace)
                event.latest_traces.append(trace_json)
#
#            # get blocked node from trace
#            if report.trace:
#                ip = report.trace.getBlockedNode().ip
#
#                # TODO: get geolocation information
#                blockedNode = EventBlockedNode()
#                blockedNode.ip = ip
#                blockedNode.city = "Unknown"
#                blockedNode.country = "Unknown"
#                blockedNode.latitude = random.randrange(-90,90,1)
#                blockedNode.longitude = random.randrange(0,180,1)
#                blockedNode.event = event
#                blockedNode.save()
#
#            # associate report to event
#            if isinstance(report, WebsiteReport):
#                eventReport = EventWebsiteReport(event=event, report=report)
#                eventReport.save()
#            elif isinstance(report, ServiceReport):
#                eventReport = EventServiceReport(event=event, report=report)
#                eventReport.save()
#
#            # save event location
#            # TODO: get location from agent ip
#            eventLocation = EventLocation()
#            eventLocation.city = "Unknown"
#            eventLocation.country = "Unknown"
#            eventLocation.latitude = random.randrange(-90,90,1)
#            eventLocation.longitude = random.randrange(0,180,1)
#            eventLocation.event = event
#            eventLocation.save()
#
        except Exception,ex:
            logging.error(ex)

        # save event
        event.save()

        # report event no notification system
        NotificationSystem.publishEvent(event)

    def updateReport(report):
        logging.info("Report received in decision system")

        print "updateReport: getEvents"

        event = Event.objects.filter(
                        location_ids__contains=report.agent_location_id,
                        last_detection_utc__gte=report.created_at-REPORT_PERIOD,
                        last_detection_utc__lte=report.created_at+REPORT_PERIOD
        )
        if not event:
            return
        event = event[0]
        print "updateReport: get event %s" % str(event)
        event.first_detection_utc = datetime.datetime.now()
        event.last_detection_utc  = datetime.datetime.now()

        if isinstance(report, WebsiteReport):
            event.target = report.url
            event.target_type = TargetType.Website
        elif isinstance(report, ServiceReport):
            event.target = report.target
            event.target_type = TargetType.Service
        else:
            raise TypeError, 'report not supported'

        event.status_code = report.status_code
        if event.status_code not in [200, 301, 302]:
            event.active = True
        else:
            event.active = False

        # TODO: get correct event type
        event.event_type = EventType.Offline

        # TODO: get isp information
        # TODO: save information about target server

        try:
            event.location_ids.append(report.agent_location_id)
            event.location_names.append(report.agent_location_name)
            event.location_country_names.append(report.agent_country_name)
            event.location_country_codes.append(report.agent_country_code)
            event.lats.append(report.agent_lat)
            event.lons.append(report.agent_lon)

            # TODO: ISP!
            event.isps.append('')
            #isps = ListField()

            if len(report.trace):
                trace = [t.get_dict() for t in report.trace]
                trace_json = json.dumps(trace)
                event.latest_traces.append(trace_json)
#
#            # get blocked node from trace
#            if report.trace:
#                ip = report.trace.getBlockedNode().ip
#
#                # TODO: get geolocation information
#                blockedNode = EventBlockedNode()
#                blockedNode.ip = ip
#                blockedNode.city = "Unknown"
#                blockedNode.country = "Unknown"
#                blockedNode.latitude = random.randrange(-90,90,1)
#                blockedNode.longitude = random.randrange(0,180,1)
#                blockedNode.event = event
#                blockedNode.save()
#
#            # associate report to event
#            if isinstance(report, WebsiteReport):
#                eventReport = EventWebsiteReport(event=event, report=report)
#                eventReport.save()
#            elif isinstance(report, ServiceReport):
#                eventReport = EventServiceReport(event=event, report=report)
#                eventReport.save()
#
#            # save event location
#            # TODO: get location from agent ip
#            eventLocation = EventLocation()
#            eventLocation.city = "Unknown"
#            eventLocation.country = "Unknown"
#            eventLocation.latitude = random.randrange(-90,90,1)
#            eventLocation.longitude = random.randrange(0,180,1)
#            eventLocation.event = event
#            eventLocation.save()
#
        except Exception,ex:
            logging.error(ex)

        # save event
        event.save()

        # report event no notification system
        NotificationSystem.publishEvent(event)

    newReport = staticmethod(newReport)
    updateReport = staticmethod(updateReport)
