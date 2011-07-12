from events.models import *
from reports.models import *
from notificationsystem.notificationsystem import NotificationSystem
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
            event.targetType = targetType.Service
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

  